from fastapi import APIRouter

from .endpoints import auth, users, languages, lessons, words, review, ai, quiz, subscriptions, support, notifications

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(languages.router, prefix="/languages", tags=["Languages"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])
api_router.include_router(words.router, prefix="/words", tags=["Words"])
api_router.include_router(review.router, prefix="/review", tags=["Review"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Conversation"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
api_router.include_router(support.router, prefix="/support", tags=["Support"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
