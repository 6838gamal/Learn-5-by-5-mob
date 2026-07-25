from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.auth_service import AuthService

router = APIRouter()


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class VerifyEmailRequest(BaseModel):
    token: str


def ok(data):
    return {"success": True, "data": data, "message": None}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.register(body.email, body.password, body.full_name)
    return ok({"id": user.id, "email": user.email, "full_name": user.full_name})


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    tokens = await service.login(body.email, body.password)
    return ok(tokens)


@router.post("/refresh")
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    tokens = await service.refresh_tokens(body.refresh_token)
    return ok(tokens)


@router.post("/logout")
async def logout(body: LogoutRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.logout(body.refresh_token)
    return ok({"message": "Logged out successfully"})


@router.post("/verify-email")
async def verify_email(body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.verify_email(body.token)
    return ok({"id": user.id, "is_verified": user.is_verified})


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return ok({
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "level": current_user.level,
        "is_verified": current_user.is_verified,
        "ui_language_id": current_user.ui_language_id,
        "target_language_id": current_user.target_language_id,
        "created_at": current_user.created_at.isoformat(),
    })
