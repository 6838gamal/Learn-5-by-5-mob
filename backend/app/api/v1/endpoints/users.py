from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import hash_password, verify_password
from app.core.exceptions import UnauthorizedError

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    timezone: str | None = None
    daily_goal_time: int | None = None
    ui_language_id: int | None = None
    target_language_id: int | None = None
    native_language_id: int | None = None
    level: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


def ok(data):
    return {"success": True, "data": data, "message": None}


@router.get("/profile")
async def get_profile(current_user=Depends(get_current_user)):
    return ok({
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "level": current_user.level,
        "timezone": current_user.timezone,
        "daily_goal_time": current_user.daily_goal_time,
        "ui_language_id": current_user.ui_language_id,
        "target_language_id": current_user.target_language_id,
    })


@router.patch("/profile")
async def update_profile(
    body: UpdateProfileRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    update_data = body.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    await db.flush()
    return ok({"updated": list(update_data.keys())})


@router.patch("/password")
async def change_password(
    body: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(body.current_password, current_user.password_hash):
        raise UnauthorizedError("Current password is incorrect.")
    current_user.password_hash = hash_password(body.new_password)
    await db.flush()
    return ok({"message": "Password updated successfully."})


@router.delete("/account")
async def delete_account(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.is_active = False
    await db.flush()
    return ok({"message": "Account deactivated."})
