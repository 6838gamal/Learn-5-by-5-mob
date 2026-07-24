from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.subscription_service import SubscriptionService

router = APIRouter()


class CheckoutRequest(BaseModel):
    plan_slug: str
    success_url: str
    cancel_url: str


def ok(data):
    return {"success": True, "data": data, "message": None}


@router.get("/plans")
async def list_plans(db: AsyncSession = Depends(get_db)):
    service = SubscriptionService(db)
    plans = await service.get_all_plans()
    return ok({"plans": [
        {
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "price_usd": float(p.price_usd),
            "billing_period": p.billing_period,
            "features": p.features,
            "ai_chat_limit": p.ai_chat_limit,
        }
        for p in plans
    ]})


@router.get("/current")
async def get_current_subscription(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)
    sub = await service.get_user_plan(current_user.id)
    if not sub:
        return ok({"subscription": None, "plan": "free"})
    return ok({
        "subscription": {
            "id": sub.id,
            "status": sub.status,
            "starts_at": sub.starts_at.isoformat(),
            "ends_at": sub.ends_at.isoformat() if sub.ends_at else None,
        },
        "plan": sub.plan.slug,
    })


@router.post("/checkout")
async def create_checkout(
    body: CheckoutRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # TODO: integrate Stripe Checkout
    # import stripe; stripe.api_key = settings.STRIPE_SECRET_KEY
    # session = stripe.checkout.Session.create(...)
    return ok({"checkout_url": "https://checkout.stripe.com/placeholder", "session_id": "placeholder"})


@router.post("/cancel")
async def cancel_subscription(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)
    sub = await service.cancel_subscription(current_user.id)
    return ok({"status": sub.status, "cancelled_at": sub.cancelled_at.isoformat()})


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    # TODO: verify Stripe signature and handle events
    payload = await request.body()
    # sig_header = request.headers.get("stripe-signature")
    return {"received": True}
