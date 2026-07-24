from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.srs_service import SRSService

router = APIRouter()


class ReviewSubmitRequest(BaseModel):
    word_id: int
    quality: int = Field(..., ge=0, le=5, description="SM-2 quality rating 0-5")


def ok(data):
    return {"success": True, "data": data, "message": None}


@router.get("/due")
async def get_due_words(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SRSService(db)
    words = await service.get_due_words(current_user.id)
    return ok({"words": [{"word_id": w.word_id, "mastery_level": w.mastery_level, "next_review_at": w.next_review_at.isoformat() if w.next_review_at else None} for w in words]})


@router.get("/count")
async def get_due_count(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SRSService(db)
    words = await service.get_due_words(current_user.id)
    return ok({"count": len(words)})


@router.post("/submit")
async def submit_review(
    body: ReviewSubmitRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SRSService(db)
    progress = await service.record_review(current_user.id, body.word_id, body.quality)
    return ok({
        "word_id": progress.word_id,
        "next_review_date": progress.next_review_at.date().isoformat() if progress.next_review_at else None,
        "interval_days": progress.interval_days,
        "mastery_level": progress.mastery_level,
    })
