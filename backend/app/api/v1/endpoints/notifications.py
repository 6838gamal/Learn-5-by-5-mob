from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.notification import Notification

router = APIRouter()


class FCMTokenRequest(BaseModel):
    fcm_token: str
    device_info: str | None = None


def ok(data):
    return {"success": True, "data": data, "message": None}


@router.get("")
async def list_notifications(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    notifications = result.scalars().all()
    return ok({"notifications": [
        {"id": n.id, "type": n.type, "title": n.title, "body": n.body, "is_read": n.is_read, "created_at": n.created_at.isoformat()}
        for n in notifications
    ]})


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == current_user.id)
        .values(is_read=True)
    )
    return ok({"updated": True})


@router.patch("/read-all")
async def mark_all_read(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    return ok({"updated": True})


@router.post("/fcm-token")
async def register_fcm_token(
    body: FCMTokenRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # TODO: store FCM token per device in a dedicated table
    return ok({"registered": True})
