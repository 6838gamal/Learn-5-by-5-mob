"""Quiz endpoint skeleton — full question generation per type to be implemented in Phase 2."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.quiz import QuizAttempt, QuizAnswer

router = APIRouter()


class StartQuizRequest(BaseModel):
    language_id: int
    quiz_type: str = "daily"   # daily / review / placement


class AnswerRequest(BaseModel):
    question_type: str
    word_id: int | None = None
    answer: dict


def ok(data):
    return {"success": True, "data": data, "message": None}


@router.post("/start", status_code=201)
async def start_quiz(
    body: StartQuizRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # TODO: generate questions based on quiz_type and today's words
    attempt = QuizAttempt(
        user_id=current_user.id,
        language_id=body.language_id,
        quiz_type=body.quiz_type,
        total_questions=7,
    )
    db.add(attempt)
    await db.flush()
    await db.refresh(attempt)
    return ok({"attempt_id": attempt.id, "total_questions": attempt.total_questions})


@router.post("/{attempt_id}/answer")
async def submit_answer(
    attempt_id: str,
    body: AnswerRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # TODO: validate answer against stored question_data, set is_correct
    answer = QuizAnswer(
        attempt_id=attempt_id,
        word_id=body.word_id,
        question_type=body.question_type,
        question_data={},
        user_answer=body.answer,
        is_correct=False,  # Placeholder
    )
    db.add(answer)
    await db.flush()
    return ok({"is_correct": answer.is_correct})


@router.post("/{attempt_id}/complete")
async def complete_quiz(
    attempt_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select, func
    result = await db.execute(select(QuizAttempt).where(QuizAttempt.id == attempt_id, QuizAttempt.user_id == current_user.id))
    attempt = result.scalar_one_or_none()
    if not attempt:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Quiz attempt")
    from datetime import datetime, timezone
    attempt.completed_at = datetime.now(timezone.utc)
    # TODO: compute score from answers
    await db.flush()
    return ok({"score": attempt.score, "correct": attempt.correct_answers, "total": attempt.total_questions})
