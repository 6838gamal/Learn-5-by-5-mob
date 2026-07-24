"""Spaced Repetition System service using the SM-2 algorithm."""
from datetime import date, datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import UserWordProgress, SpacedRepetitionSchedule
from app.repositories.progress_repository import UserWordProgressRepository


class SRSService:
    """
    SM-2 Algorithm implementation.
    quality: 0-5 (0=complete blackout, 5=perfect response)
    """

    MIN_EASE = 1.3

    def __init__(self, db: AsyncSession):
        self.db = db
        self.progress_repo = UserWordProgressRepository(db)

    async def get_due_words(self, user_id: str) -> list[UserWordProgress]:
        return await self.progress_repo.get_due_for_review(user_id)

    async def record_review(self, user_id: str, word_id: int, quality: int) -> UserWordProgress:
        """Apply SM-2 and update next review date. quality must be 0-5."""
        quality = max(0, min(5, quality))
        progress = await self.progress_repo.get_for_word(user_id, word_id)

        if not progress:
            progress = UserWordProgress(user_id=user_id, word_id=word_id)
            self.db.add(progress)

        now = datetime.now(timezone.utc)
        progress.last_reviewed_at = now
        progress.repetitions += 1

        if quality >= 3:
            progress.correct_count += 1
            if progress.repetitions == 1:
                new_interval = 1
            elif progress.repetitions == 2:
                new_interval = 6
            else:
                new_interval = round(progress.interval_days * progress.ease_factor)

            new_ef = progress.ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
            progress.ease_factor = max(self.MIN_EASE, new_ef)
            progress.interval_days = new_interval
            progress.mastery_level = min(5, progress.mastery_level + 1)
        else:
            progress.incorrect_count += 1
            progress.repetitions = 0
            progress.interval_days = 1
            progress.mastery_level = max(0, progress.mastery_level - 1)

        progress.next_review_at = now + timedelta(days=progress.interval_days)

        # Log schedule entry
        schedule = SpacedRepetitionSchedule(
            user_id=user_id,
            word_id=word_id,
            scheduled_date=progress.next_review_at.date(),
            is_done=True,
            quality_rating=quality,
            reviewed_at=now,
        )
        self.db.add(schedule)
        await self.db.flush()
        return progress

    async def schedule_new_words(self, user_id: str, word_ids: list[int]) -> None:
        """Register newly learned words into the SRS system."""
        tomorrow = date.today() + timedelta(days=1)
        for word_id in word_ids:
            existing = await self.progress_repo.get_for_word(user_id, word_id)
            if not existing:
                progress = UserWordProgress(
                    user_id=user_id,
                    word_id=word_id,
                    next_review_at=datetime.combine(tomorrow, datetime.min.time()).replace(tzinfo=timezone.utc),
                )
                self.db.add(progress)
        await self.db.flush()
