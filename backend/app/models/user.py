import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))

    ui_language_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("languages.id"))
    target_language_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("languages.id"))
    native_language_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("languages.id"))

    level: Mapped[str] = mapped_column(String(20), default="beginner", nullable=False)
    timezone: Mapped[str | None] = mapped_column(String(50))
    daily_goal_time: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_token: Mapped[str | None] = mapped_column(String(255))

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    lesson_progress: Mapped[list] = relationship("UserLessonProgress", back_populates="user", cascade="all, delete-orphan")
    word_progress: Mapped[list] = relationship("UserWordProgress", back_populates="user", cascade="all, delete-orphan")
    srs_schedules: Mapped[list] = relationship("SpacedRepetitionSchedule", back_populates="user", cascade="all, delete-orphan")
    ai_conversations: Mapped[list] = relationship("AIConversation", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts: Mapped[list] = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    subscriptions: Mapped[list] = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    support_tickets: Mapped[list] = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    device_info: Mapped[str | None] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
