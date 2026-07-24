"""Seed script — run once after initial migration to populate reference data."""
import asyncio
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.language import Language
from app.models.subscription import SubscriptionPlan
from app.models.admin import AdminUser


LANGUAGES = [
    {"code": "en", "name_en": "English",  "name_native": "English", "rtl": False, "is_ui_lang": True,  "is_target": True},
    {"code": "ar", "name_en": "Arabic",   "name_native": "العربية", "rtl": True,  "is_ui_lang": True,  "is_target": True},
    {"code": "fr", "name_en": "French",   "name_native": "Français","rtl": False, "is_ui_lang": True,  "is_target": True},
    {"code": "es", "name_en": "Spanish",  "name_native": "Español", "rtl": False, "is_ui_lang": True,  "is_target": True},
    {"code": "de", "name_en": "German",   "name_native": "Deutsch", "rtl": False, "is_ui_lang": True,  "is_target": True},
]

PLANS = [
    {
        "name": "Free",
        "slug": "free",
        "price_usd": 0.00,
        "billing_period": None,
        "ai_chat_limit": 3,
        "lesson_limit": 1,
        "features": {
            "daily_lesson": True,
            "basic_review": True,
            "ai_chat": True,
            "ai_chat_limit_per_day": 3,
            "advanced_stats": False,
            "unlimited_review": False,
        },
    },
    {
        "name": "Premium",
        "slug": "premium",
        "price_usd": 9.99,
        "billing_period": "monthly",
        "ai_chat_limit": None,
        "lesson_limit": None,
        "features": {
            "daily_lesson": True,
            "basic_review": True,
            "ai_chat": True,
            "ai_chat_limit_per_day": None,
            "advanced_stats": True,
            "unlimited_review": True,
            "all_scenarios": True,
        },
    },
    {
        "name": "Lifetime",
        "slug": "lifetime",
        "price_usd": 149.99,
        "billing_period": "once",
        "ai_chat_limit": None,
        "lesson_limit": None,
        "features": {
            "daily_lesson": True,
            "basic_review": True,
            "ai_chat": True,
            "ai_chat_limit_per_day": None,
            "advanced_stats": True,
            "unlimited_review": True,
            "all_scenarios": True,
            "lifetime_updates": True,
        },
    },
]


async def seed():
    async with AsyncSessionLocal() as db:
        # Languages
        from sqlalchemy import select
        existing = await db.execute(select(Language))
        if not existing.scalars().first():
            for lang_data in LANGUAGES:
                db.add(Language(**lang_data))
            print("✓ Languages seeded")
        else:
            print("· Languages already exist, skipping")

        # Subscription plans
        existing_plans = await db.execute(select(SubscriptionPlan))
        if not existing_plans.scalars().first():
            for plan_data in PLANS:
                db.add(SubscriptionPlan(**plan_data))
            print("✓ Subscription plans seeded")
        else:
            print("· Plans already exist, skipping")

        # Default admin user
        existing_admin = await db.execute(select(AdminUser))
        if not existing_admin.scalars().first():
            admin = AdminUser(
                email="admin@learn5by5.com",
                password_hash=hash_password("changeme123"),
                full_name="Admin",
            )
            db.add(admin)
            print("✓ Default admin created — email: admin@learn5by5.com / password: changeme123")
            print("  ⚠️  Change the admin password immediately after first login!")
        else:
            print("· Admin already exists, skipping")

        await db.commit()
    print("\n✅ Seed complete")


if __name__ == "__main__":
    asyncio.run(seed())
