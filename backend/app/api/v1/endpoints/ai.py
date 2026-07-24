from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.models.ai import AIConversation
from app.services.ai_service import AIService

router = APIRouter()


def ok(data):
    return {"success": True, "data": data, "message": None}


@router.post("/conversation/start")
async def start_conversation(
    language_id: int = Form(...),
    scenario_id: int | None = Form(None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.word_repository import WordRepository
    from app.models.lesson import Scenario
    import datetime

    word_repo = WordRepository(db)
    today = datetime.date.today()
    words = await word_repo.get_daily_words(language_id, today)
    word_strs = [w.word for w in words]

    scenario_title = None
    if scenario_id:
        result = await db.execute(select(Scenario).where(Scenario.id == scenario_id))
        scenario = result.scalar_one_or_none()
        if scenario:
            scenario_title = scenario.title

    # TODO: get language name from DB
    language_name = "English"

    service = AIService(db)
    conversation = await service.start_conversation(
        user_id=current_user.id,
        language_id=language_id,
        language_name=language_name,
        today_words=word_strs,
        scenario_id=scenario_id,
        scenario_title=scenario_title,
        lesson_date=today,
    )
    return ok({"conversation_id": conversation.id, "status": conversation.status})


@router.post("/conversation/{conversation_id}/message")
async def send_message(
    conversation_id: str,
    audio: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AIConversation).where(
            AIConversation.id == conversation_id,
            AIConversation.user_id == current_user.id,
            AIConversation.status == "active",
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise NotFoundError("Conversation")

    audio_bytes = await audio.read()
    service = AIService(db)
    response = await service.process_audio_message(
        conversation=conversation,
        audio_bytes=audio_bytes,
        language_name="English",  # TODO: resolve from DB
        today_words=[],           # TODO: load from lesson
        scenario_title=None,
    )
    return ok(response)


@router.post("/conversation/{conversation_id}/end")
async def end_conversation(
    conversation_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AIConversation).where(
            AIConversation.id == conversation_id,
            AIConversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise NotFoundError("Conversation")

    service = AIService(db)
    feedback = await service.end_conversation(conversation)
    return ok(feedback)
