"""Authentication service — register, login, token refresh, password reset."""
import hashlib
from datetime import datetime, timezone, timedelta

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

    async def verify_email(self, token: str) -> User:
        user = await self.user_repo.get_by_verification_token(token)
        if not user:
            raise NotFoundError("Verification token")
        user.is_verified = True
        user.verification_token = None
        await self.db.flush()
        return user
