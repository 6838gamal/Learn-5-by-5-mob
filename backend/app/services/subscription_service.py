"""Subscription service — plan management and feature gating."""
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import SubscriptionRequiredError, NotFoundError
from app.models.subscription import Subscription
from app.repositories.subscription_repository import SubscriptionRepository


class SubscriptionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SubscriptionRepository(db)

    async def get_user_plan(self, user_id: str) -> Subscription | None:
        return await self.repo.get_active_for_user(user_id)

    async def get_all_plans(self) -> list:
        return await self.repo.get_all_plans()

    async def is_premium(self, user_id: str) -> bool:
        sub = await self.repo.get_active_for_user(user_id)
        if not sub:
            return False
        return sub.plan.slug in ("premium", "lifetime")

    async def require_premium(self, user_id: str, feature: str = "this feature") -> None:
        if not await self.is_premium(user_id):
            raise SubscriptionRequiredError(feature)

    async def check_ai_limit(self, user_id: str, used_today: int) -> bool:
        """Returns True if user can start an AI conversation."""
        sub = await self.repo.get_active_for_user(user_id)
        if not sub:
            # Free plan — use default limit
            limit = 3
        else:
            limit = sub.plan.ai_chat_limit  # None = unlimited
        if limit is None:
            return True
        return used_today < limit

    async def activate_subscription(
        self,
        user_id: str,
        plan_slug: str,
        external_id: str,
        starts_at: datetime,
        ends_at: datetime | None = None,
    ) -> Subscription:
        plan = await self.repo.get_plan_by_slug(plan_slug)
        if not plan:
            raise NotFoundError("Subscription plan")

        sub = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            status="active",
            external_id=external_id,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        return await self.repo.create(sub)

    async def cancel_subscription(self, user_id: str) -> Subscription:
        sub = await self.repo.get_active_for_user(user_id)
        if not sub:
            raise NotFoundError("Active subscription")
        sub.status = "cancelled"
        sub.cancelled_at = datetime.now(timezone.utc)
        await self.db.flush()
        return sub
