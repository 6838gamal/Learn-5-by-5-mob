# Import all models here so Alembic can detect them
from .user import User, RefreshToken
from .language import Language
from .word import Word, WordCategory, WordTranslation, WordExample
from .lesson import DailyLessonWord, Scenario, UserLessonProgress
from .progress import UserWordProgress, SpacedRepetitionSchedule
from .ai import AIConversation, AIMessage
from .quiz import QuizAttempt, QuizAnswer
from .subscription import SubscriptionPlan, Subscription
from .support import SupportTicket, SupportMessage
from .notification import Notification
from .settings import AppSetting
from .admin import AdminUser

__all__ = [
    "User", "RefreshToken",
    "Language",
    "Word", "WordCategory", "WordTranslation", "WordExample",
    "DailyLessonWord", "Scenario", "UserLessonProgress",
    "UserWordProgress", "SpacedRepetitionSchedule",
    "AIConversation", "AIMessage",
    "QuizAttempt", "QuizAnswer",
    "SubscriptionPlan", "Subscription",
    "SupportTicket", "SupportMessage",
    "Notification",
    "AppSetting",
    "AdminUser",
]
