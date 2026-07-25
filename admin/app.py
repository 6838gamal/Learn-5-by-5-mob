"""Admin dashboard — FastAPI + Jinja2 + HTMX + Alpine.js + Tailwind CSS."""
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import os
from app.core.config import settings

admin_app = FastAPI(title="Learn 5 by 5 — Admin", docs_url=None, redoc_url=None)
admin_app.add_middleware(SessionMiddleware, secret_key=settings.ADMIN_SESSION_SECRET)

_here = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(_here, "templates"))

os.makedirs(os.path.join(_here, "static"), exist_ok=True)
admin_app.mount("/static", StaticFiles(directory=os.path.join(_here, "static")), name="admin-static")


# ── Auth helpers ──────────────────────────────────────────────────────────────

def get_admin_user(request: Request):
    if not request.session.get("admin_id"):
        raise HTTPException(status_code=302, headers={"Location": "/admin/login"})
    return request.session["admin_id"]


# ── Auth routes ───────────────────────────────────────────────────────────────

@admin_app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@admin_app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    from app.core.database import AsyncSessionLocal
    from app.models.admin import AdminUser
    from app.core.security import verify_password
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AdminUser).where(AdminUser.email == email))
        admin = result.scalar_one_or_none()
        if not admin or not verify_password(password, admin.password_hash):
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Invalid credentials"},
                status_code=401,
            )
        request.session["admin_id"] = admin.id
        request.session["admin_email"] = admin.email
        request.session["admin_name"] = admin.full_name or admin.email
    return RedirectResponse(url="/admin/dashboard", status_code=302)


@admin_app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=302)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, admin=Depends(get_admin_user)):
    # TODO: load real metrics from DB
    metrics = {
        "total_users": 0,
        "active_today": 0,
        "revenue_month": 0,
        "active_subscriptions": 0,
        "ai_conversations_today": 0,
        "lessons_completed_today": 0,
    }
    return templates.TemplateResponse("dashboard/index.html", {"request": request, "metrics": metrics})


# ── Users ─────────────────────────────────────────────────────────────────────

@admin_app.get("/users", response_class=HTMLResponse)
async def users_list(request: Request, admin=Depends(get_admin_user), q: str = "", page: int = 1):
    from app.core.database import AsyncSessionLocal
    from app.models.user import User
    from sqlalchemy import select, or_

    async with AsyncSessionLocal() as db:
        stmt = select(User).order_by(User.created_at.desc()).limit(30).offset((page - 1) * 30)
        if q:
            stmt = stmt.where(or_(User.email.ilike(f"%{q}%"), User.full_name.ilike(f"%{q}%")))
        result = await db.execute(stmt)
        users = result.scalars().all()

    return templates.TemplateResponse("users/list.html", {"request": request, "users": users, "q": q, "page": page})


@admin_app.get("/users/{user_id}", response_class=HTMLResponse)
async def user_detail(user_id: str, request: Request, admin=Depends(get_admin_user)):
    from app.core.database import AsyncSessionLocal
    from app.models.user import User
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404)

    return templates.TemplateResponse("users/detail.html", {"request": request, "user": user})


# ── Content ───────────────────────────────────────────────────────────────────

@admin_app.get("/content/words", response_class=HTMLResponse)
async def words_list(request: Request, admin=Depends(get_admin_user), language_id: int = 1, page: int = 1):
    from app.core.database import AsyncSessionLocal
    from app.models.word import Word
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Word).where(Word.language_id == language_id, Word.is_active == True)
            .order_by(Word.id).limit(30).offset((page - 1) * 30)
        )
        words = result.scalars().all()

    return templates.TemplateResponse("content/words.html", {"request": request, "words": words, "language_id": language_id, "page": page})


@admin_app.get("/content/daily-lessons", response_class=HTMLResponse)
async def daily_lessons(request: Request, admin=Depends(get_admin_user)):
    return templates.TemplateResponse("content/daily_lessons.html", {"request": request})


# ── Support ───────────────────────────────────────────────────────────────────

@admin_app.get("/support/tickets", response_class=HTMLResponse)
async def support_tickets(request: Request, admin=Depends(get_admin_user), status_filter: str = "open"):
    from app.core.database import AsyncSessionLocal
    from app.models.support import SupportTicket
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        stmt = select(SupportTicket).order_by(SupportTicket.created_at.desc()).limit(50)
        if status_filter != "all":
            stmt = stmt.where(SupportTicket.status == status_filter)
        result = await db.execute(stmt)
        tickets = result.scalars().all()

    return templates.TemplateResponse("support/tickets.html", {"request": request, "tickets": tickets, "status_filter": status_filter})


@admin_app.get("/support/tickets/{ticket_id}", response_class=HTMLResponse)
async def support_ticket_detail(ticket_id: str, request: Request, admin=Depends(get_admin_user)):
    from app.core.database import AsyncSessionLocal
    from app.models.support import SupportTicket, SupportMessage
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
        ticket = result.scalar_one_or_none()
        if not ticket:
            raise HTTPException(status_code=404)
        msgs = await db.execute(select(SupportMessage).where(SupportMessage.ticket_id == ticket_id).order_by(SupportMessage.created_at))
        messages = msgs.scalars().all()

    return templates.TemplateResponse("support/ticket_detail.html", {"request": request, "ticket": ticket, "messages": messages})


@admin_app.post("/support/tickets/{ticket_id}/reply")
async def support_reply(ticket_id: str, request: Request, content: str = Form(...), admin=Depends(get_admin_user)):
    from app.core.database import AsyncSessionLocal
    from app.models.support import SupportMessage

    async with AsyncSessionLocal() as db:
        msg = SupportMessage(
            ticket_id=ticket_id,
            sender_type="admin",
            sender_id=str(request.session.get("admin_id")),
            content=content,
        )
        db.add(msg)
        await db.commit()

    return RedirectResponse(url=f"/admin/support/tickets/{ticket_id}", status_code=302)


# ── Subscriptions ─────────────────────────────────────────────────────────────

@admin_app.get("/subscriptions/plans", response_class=HTMLResponse)
async def subscription_plans(request: Request, admin=Depends(get_admin_user)):
    from app.core.database import AsyncSessionLocal
    from app.models.subscription import SubscriptionPlan
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(SubscriptionPlan))
        plans = result.scalars().all()

    return templates.TemplateResponse("subscriptions/plans.html", {"request": request, "plans": plans})


# ── Notifications ─────────────────────────────────────────────────────────────

@admin_app.get("/notifications", response_class=HTMLResponse)
async def notifications_page(request: Request, admin=Depends(get_admin_user)):
    return templates.TemplateResponse("notifications/send.html", {"request": request})


# ── Settings ──────────────────────────────────────────────────────────────────

@admin_app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, admin=Depends(get_admin_user)):
    return templates.TemplateResponse("settings/index.html", {"request": request})
