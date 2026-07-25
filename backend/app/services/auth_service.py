"""Authentication service — register, login, Google SSO, token refresh, password reset."""
import hashlib
import secrets
from datetime import datetime, timezone, timedelta

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    generate_secure_token, decode_token,
)
from app.core.config import settings
from app.core.exceptions import UnauthorizedError, ConflictError, NotFoundError
from app.models.user import User, RefreshToken
from app.repositories.user_repository import UserRepository

_GOOGLE_TOKENINFO_URL  = "https://oauth2.googleapis.com/tokeninfo"
_GOOGLE_USERINFO_URL   = "https://www.googleapis.com/oauth2/v3/userinfo"


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, email: str, password: str, full_name: str | None = None) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ConflictError("An account with this email already exists.")

        verification_token = generate_secure_token()
        user = User(
            email=email.lower().strip(),
            password_hash=hash_password(password),
            full_name=full_name,
            verification_token=verification_token,
        )
        await self.user_repo.create(user)
        # TODO: send verification email
        return user

    async def login(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email.lower().strip())
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedError("Account is suspended.")

        access_token = create_access_token(user.id)
        raw_refresh, refresh_hash = create_refresh_token(user.id)

        rt = RefreshToken(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self.user_repo.save_refresh_token(rt)
        await self.user_repo.update_last_login(user.id)

        return {
            "access_token": access_token,
            "refresh_token": raw_refresh,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def refresh_tokens(self, raw_refresh_token: str) -> dict:
        token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
        try:
            payload = decode_token(raw_refresh_token)
        except ValueError:
            raise UnauthorizedError("Invalid or expired refresh token.")

        if payload.get("type") != "refresh":
            raise UnauthorizedError("Wrong token type.")

        stored = await self.user_repo.get_refresh_token_by_hash(token_hash)
        if not stored:
            raise UnauthorizedError("Refresh token has been revoked.")

        user_id = payload["sub"]
        new_access = create_access_token(user_id)
        new_raw_refresh, new_hash = create_refresh_token(user_id)

        # Rotate refresh token
        await self.user_repo.revoke_refresh_token(token_hash)
        rt = RefreshToken(
            user_id=user_id,
            token_hash=new_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self.user_repo.save_refresh_token(rt)

        return {
            "access_token": new_access,
            "refresh_token": new_raw_refresh,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def logout(self, raw_refresh_token: str) -> None:
        token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
        await self.user_repo.revoke_refresh_token(token_hash)

    # ------------------------------------------------------------------
    # Google Sign-In
    # ------------------------------------------------------------------

    async def login_with_google(
        self,
        *,
        id_token: str | None = None,
        access_token: str | None = None,
    ) -> dict:
        """Verify a Google credential and return app JWT tokens.

        Accepts either an id_token (preferred on web) or an access_token
        (fallback).  Creates the user account on first login.
        """
        google_user = await self._fetch_google_user(
            id_token=id_token, access_token=access_token
        )

        email: str = google_user["email"].lower().strip()
        if not email:
            raise UnauthorizedError("Google account has no email address.")

        user = await self.user_repo.get_by_email(email)
        if user is None:
            # First-time Google login — create the account
            user = User(
                email=email,
                # Google accounts don't have a password; store a random,
                # never-usable hash so the NOT NULL constraint is satisfied.
                password_hash=hash_password(secrets.token_urlsafe(32)),
                full_name=google_user.get("name"),
                avatar_url=google_user.get("picture"),
                is_verified=True,   # Google already verified the email
            )
            await self.user_repo.create(user)
        else:
            # Returning user — refresh avatar / name if provided
            updated = False
            if google_user.get("picture") and user.avatar_url != google_user["picture"]:
                user.avatar_url = google_user["picture"]
                updated = True
            if google_user.get("name") and not user.full_name:
                user.full_name = google_user["name"]
                updated = True
            if updated:
                await self.db.flush()

        if not user.is_active:
            raise UnauthorizedError("Account is suspended.")

        access  = create_access_token(user.id)
        raw_rt, rt_hash = create_refresh_token(user.id)

        rt = RefreshToken(
            user_id=user.id,
            token_hash=rt_hash,
            expires_at=datetime.now(timezone.utc)
                       + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self.user_repo.save_refresh_token(rt)
        await self.user_repo.update_last_login(user.id)

        return {
            "access_token": access,
            "refresh_token": raw_rt,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def _fetch_google_user(
        self,
        *,
        id_token: str | None,
        access_token: str | None,
    ) -> dict:
        """Call Google's public API to validate the credential and return profile info."""
        async with httpx.AsyncClient(timeout=10) as client:
            if id_token:
                resp = await client.get(
                    _GOOGLE_TOKENINFO_URL, params={"id_token": id_token}
                )
                if resp.status_code != 200:
                    raise UnauthorizedError("Invalid Google id_token.")
                data = resp.json()
                return {
                    "email":   data.get("email", ""),
                    "name":    data.get("name"),
                    "picture": data.get("picture"),
                }

            if access_token:
                resp = await client.get(
                    _GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if resp.status_code != 200:
                    raise UnauthorizedError("Invalid Google access_token.")
                data = resp.json()
                return {
                    "email":   data.get("email", ""),
                    "name":    data.get("name"),
                    "picture": data.get("picture"),
                }

        raise UnauthorizedError("No Google credential provided.")

    # ------------------------------------------------------------------

    async def verify_email(self, token: str) -> User:
        user = await self.user_repo.get_by_verification_token(token)
        if not user:
            raise NotFoundError("Verification token")
        user.is_verified = True
        user.verification_token = None
        await self.db.flush()
        return user
