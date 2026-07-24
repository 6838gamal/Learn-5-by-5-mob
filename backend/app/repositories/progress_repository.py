from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.progress import UserWordProgress, SpacedRepetitionSchedule
from app.models.lesson import UserLessonProgress
from .base import BaseRepository


class UserLessonProgressRepository(BaseRepository[UserLessonProgress]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserLessonProgress, db)

    async def get_for_user_date(self, user_id: str, lesson_date: date, language_id: int) -> UserLessonProgress | None:
        result = await self.db.execute(
            select(UserLessonProgress).where(
                and_(
                    UserLessonProgress.user_id == user_id,
                    UserLessonProgress.lesson_date == lesson_date,
                    UserLessonProgress.language_id == language_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_streak(self, user_id: str, language_id: int) -> int:
        """Count consecutive completed days ending today."""
        from sqlalchemy import func, desc
        result = await self.db.execute(
            select(UserLessonProgress.lesson_date)
            .where(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.language_id == language_id,
                UserLessonProgress.is_complete == True,
            )
            .order_by(desc(UserLessonProgress.lesson_date))
        )
        dates = [row[0] for row in result.all()]
        streak = 0
        expected = date.today()
        for d in dates:
            if d == expected:
                streak += 1
                from datetime import timedelta
                expected = expected - timedelta(days=1)
            else:
                break
        return streak


class UserWordProgressRepository(BaseRepository[UserWordProgress]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserWordProgress, db)

    async def get_for_word(self, user_id: str, word_id: int) -> UserWordProgress | None:
        result = await self.db.execute(
            select(UserWordProgress).where(
                UserWordProgress.user_id == user_id,
                UserWordProgress.word_id == word_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_due_for_review(self, user_id: str) -> list[UserWordProgress]:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(UserWordProgress).where(
                UserWordProgress.user_id == user_id,
                UserWordProgress.next_review_at <= now,
            )
        )
        return list(result.scalars().all())
