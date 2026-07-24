from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.word import Word, WordCategory, WordTranslation, WordExample
from app.models.lesson import DailyLessonWord
from .base import BaseRepository


class WordRepository(BaseRepository[Word]):
    def __init__(self, db: AsyncSession):
        super().__init__(Word, db)

    async def get_with_details(self, word_id: int) -> Word | None:
        result = await self.db.execute(
            select(Word)
            .options(selectinload(Word.translations), selectinload(Word.examples), selectinload(Word.category))
            .where(Word.id == word_id, Word.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_daily_words(self, language_id: int, lesson_date: date) -> list[Word]:
        result = await self.db.execute(
            select(Word)
            .join(DailyLessonWord, DailyLessonWord.word_id == Word.id)
            .options(selectinload(Word.translations), selectinload(Word.examples))
            .where(
                DailyLessonWord.language_id == language_id,
                DailyLessonWord.lesson_date == lesson_date,
            )
            .order_by(DailyLessonWord.sort_order)
        )
        return list(result.scalars().all())

    async def search(self, language_id: int, query: str, limit: int = 20) -> list[Word]:
        result = await self.db.execute(
            select(Word)
            .where(Word.language_id == language_id, Word.word.ilike(f"%{query}%"), Word.is_active == True)
            .limit(limit)
        )
        return list(result.scalars().all())
