"""Lesson service — daily lesson loading, progress tracking, streak calculation."""
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.lesson import UserLessonProgress
from app.repositories.word_repository import WordRepository
from app.repositories.progress_repository import UserLessonProgressRepository


class LessonService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.word_repo = WordRepository(db)
        self.progress_repo = UserLessonProgressRepository(db)

    async def get_today_lesson(self, user_id: str, language_id: int) -> dict:
        today = date.today()
        words = await self.word_repo.get_daily_words(language_id, today)
        if not words:
            raise NotFoundError("Lesson for today")

        progress = await self.progress_repo.get_for_user_date(user_id, today, language_id)
        if not progress:
            progress = UserLessonProgress(
                user_id=user_id,
                lesson_date=today,
                language_id=language_id,
            )
            await self.progress_repo.create(progress)

        return {
            "lesson_date": today.isoformat(),
            "language_id": language_id,
            "words": words,
            "progress": progress,
        }

    async def update_step(self, user_id: str, language_id: int, step: int) -> UserLessonProgress:
        today = date.today()
        progress = await self.progress_repo.get_for_user_date(user_id, today, language_id)
        if not progress:
            raise NotFoundError("Lesson progress")

        progress.step_completed = max(progress.step_completed, step)
        if step >= 11 and not progress.is_complete:
            progress.is_complete = True
            progress.completed_at = datetime.now(timezone.utc)

        await self.db.flush()
        return progress

    async def get_streak(self, user_id: str, language_id: int) -> int:
        return await self.progress_repo.get_streak(user_id, language_id)
