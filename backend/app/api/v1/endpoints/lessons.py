from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.lesson_service import LessonService

router = APIRouter()


class UpdateStepRequest(BaseModel):
    language_id: int
    step: int  # 1-11


def ok(data):
    return {"success": True, "data": data, "message": None}


@router.get("/today")
async def get_today_lesson(
    language_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = LessonService(db)
    lesson = await service.get_today_lesson(current_user.id, language_id)
    return ok(lesson)


@router.post("/progress")
async def update_progress(
    body: UpdateStepRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = LessonService(db)
    progress = await service.update_step(current_user.id, body.language_id, body.step)
    return ok({
        "step_completed": progress.step_completed,
        "is_complete": progress.is_complete,
        "xp_earned": progress.xp_earned,
    })


@router.get("/streak")
async def get_streak(
    language_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = LessonService(db)
    streak = await service.get_streak(current_user.id, language_id)
    return ok({"streak_days": streak})
