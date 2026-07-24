from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Language(Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(5), unique=True, nullable=False)   # en, ar, fr, es, de
    name_en: Mapped[str] = mapped_column(String(50), nullable=False)
    name_native: Mapped[str] = mapped_column(String(50), nullable=False)
    is_ui_lang: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_target: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rtl: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
