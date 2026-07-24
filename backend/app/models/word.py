from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Integer, SmallInteger, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class WordCategory(Base):
    __tablename__ = "word_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    words: Mapped[list["Word"]] = relationship("Word", back_populates="category")


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    language_id: Mapped[int] = mapped_column(Integer, ForeignKey("languages.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("word_categories.id"))
    word: Mapped[str] = mapped_column(String(100), nullable=False)
    phonetic: Mapped[str | None] = mapped_column(String(100))
    audio_url: Mapped[str | None] = mapped_column(String(500))
    difficulty: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    part_of_speech: Mapped[str | None] = mapped_column(String(30))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    category: Mapped["WordCategory | None"] = relationship("WordCategory", back_populates="words")
    translations: Mapped[list["WordTranslation"]] = relationship("WordTranslation", back_populates="word", cascade="all, delete-orphan")
    examples: Mapped[list["WordExample"]] = relationship("WordExample", back_populates="word", cascade="all, delete-orphan", order_by="WordExample.sort_order")
    user_progress: Mapped[list] = relationship("UserWordProgress", back_populates="word")


class WordTranslation(Base):
    __tablename__ = "word_translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    word_id: Mapped[int] = mapped_column(Integer, ForeignKey("words.id", ondelete="CASCADE"), nullable=False)
    language_id: Mapped[int] = mapped_column(Integer, ForeignKey("languages.id"), nullable=False)
    meaning: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    word: Mapped["Word"] = relationship("Word", back_populates="translations")


class WordExample(Base):
    __tablename__ = "word_examples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    word_id: Mapped[int] = mapped_column(Integer, ForeignKey("words.id", ondelete="CASCADE"), nullable=False)
    sentence: Mapped[str] = mapped_column(Text, nullable=False)
    translation: Mapped[str | None] = mapped_column(Text)
    audio_url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    word: Mapped["Word"] = relationship("Word", back_populates="examples")
