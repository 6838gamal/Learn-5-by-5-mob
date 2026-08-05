"""Admin dashboard — FastAPI + Jinja2 + HTMX + Alpine.js + Tailwind CSS.

Auth: admin submits credentials → backend POST /admin/auth/login → JWT token stored in session.
All subsequent API calls use that token via Authorization: Bearer.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import httpx
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings

# ── App setup ─────────────────────────────────────────────────────────────────

settings = get_settings()

admin_app = FastAPI(title="Learn 5 by 5 — Admin", docs_url=None, redoc_url=None)
admin_app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="l5b5_admin_session",
    same_site="lax",
    https_only=False,
    max_age=60 * 60 * 8,  # 8 hours
)

_here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(_here, "static"), exist_ok=True)
admin_app.mount("/static", StaticFiles(directory=os.path.join(_here, "static")), name="admin-static")

templates = Jinja2Templates(directory=os.path.join(_here, "templates"))


# ── Jinja2 custom filters ─────────────────────────────────────────────────────

def _fmt_date(value: str | None, fmt: str = "%Y-%m-%d") -> str:
    """Format an ISO date string. Returns '—' if None or unparseable."""
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.strftime(fmt)
    except Exception:
        return str(value)[:10]


def _fmt_datetime(value: str | None) -> str:
    return _fmt_date(value, "%Y-%m-%d %H:%M")


def _currency(value: Any) -> str:
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return str(value)


templates.env.filters["fmt_date"] = _fmt_date
templates.env.filters["fmt_datetime"] = _fmt_datetime
templates.env.filters["currency"] = _currency


# ── API client helpers ────────────────────────────────────────────────────────

class AdminApiError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


def _make_client(token: str | None = None) -> httpx.AsyncClient:
    headers: dict[str, str] = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return httpx.AsyncClient(base_url=settings.API_BASE_URL, headers=headers, timeout=30)


async def _api(client: httpx.AsyncClient, method: str, path: str, **kwargs) -> Any:
    resp = await getattr(client, method)(path, **kwargs)
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise AdminApiError(resp.status_code, str(detail))
    try:
        return resp.json()
    except Exception:
        return {}


async def _safe_get(client: httpx.AsyncClient, path: str, params: dict | None = None) -> Any:
    """GET with graceful fallback — returns None on error."""
    try:
        return await _api(client, "get", path, params=params)
    except (AdminApiError, httpx.HTTPError):
        return None


# ── Auth helpers ──────────────────────────────────────────────────────────────

def get_admin_token(request: Request) -> str:
    token = request.session.get("admin_token")
    if not token:
        raise HTTPException(status_code=302, headers={"Location": "/admin/login"})
    return token


def get_admin_name(request: Request) -> str:
    return request.session.get("admin_name", "Admin")


# ── Auth routes ───────────────────────────────────────────────────────────────

@admin_app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("admin_token"):
        return RedirectResponse("/admin/dashboard", status_code=302)
    return templates.TemplateResponse(request, "auth/login.html", {"error": None})


@admin_app.post("/login", response_class=HTMLResponse)
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    async with _make_client() as client:
        try:
            resp = await _api(client, "post", "/admin/auth/login",
                              json={"email": email, "password": password},
                              headers={"Content-Type": "application/json"})
            data = resp.get("data", resp) if isinstance(resp, dict) else resp
            token = data.get("access_token") or data.get("token")
            name = data.get("name") or data.get("full_name") or email
            if not token:
                raise AdminApiError(401, "No token in response")
        except AdminApiError as e:
            return templates.TemplateResponse(request, "auth/login.html",
                                              {"error": "Invalid credentials or server error: " + e.detail},
                                              status_code=401)
        except httpx.HTTPError as e:
            return templates.TemplateResponse(request, "auth/login.html",
                                              {"error": "Cannot reach server. Try again later."},
                                              status_code=503)

    request.session["admin_token"] = token
    request.session["admin_name"] = name
    request.session["admin_email"] = email
    return RedirectResponse("/admin/dashboard", status_code=302)


@admin_app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=302)


# ── Root redirect ─────────────────────────────────────────────────────────────

@admin_app.get("/")
async def root():
    return RedirectResponse("/admin/dashboard", status_code=302)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, token: str = Depends(get_admin_token)):
    metrics: dict = {
        "total_users": "—",
        "active_today": "—",
        "revenue_month": "—",
        "active_subscriptions": "—",
        "ai_conversations_today": "—",
        "lessons_completed_today": "—",
    }
    growth: list = []
    recent_users: list = []

    async with _make_client(token) as client:
        stats_resp = await _safe_get(client, "/admin/stats")
        if stats_resp:
            data = stats_resp.get("data", stats_resp) if isinstance(stats_resp, dict) else {}
            metrics.update({k: v for k, v in data.items() if k in metrics})
            growth = data.get("daily_active_users", data.get("growth", []))

        users_resp = await _safe_get(client, "/admin/users", params={"limit": 5, "page": 1})
        if users_resp:
            d = users_resp.get("data", users_resp) if isinstance(users_resp, dict) else {}
            recent_users = d.get("users", d.get("items", []))[:5] if isinstance(d, dict) else []

    return templates.TemplateResponse(request, "dashboard/index.html", {
        "metrics": metrics,
        "growth": growth,
        "recent_users": recent_users,
        "admin_name": get_admin_name(request),
        "active_nav": "dashboard",
    })


# ── Users ─────────────────────────────────────────────────────────────────────

@admin_app.get("/users", response_class=HTMLResponse)
async def users_list(request: Request, token: str = Depends(get_admin_token),
                     q: str = "", page: int = 1, status: str = "all"):
    users: list = []
    total = 0
    error = None

    async with _make_client(token) as client:
        params: dict = {"page": page, "limit": 30}
        if q:
            params["q"] = q
        if status != "all":
            params["status"] = status

        resp = await _safe_get(client, "/admin/users", params=params)
        if resp:
            data = resp.get("data", resp) if isinstance(resp, dict) else {}
            if isinstance(data, dict):
                users = data.get("users", data.get("items", []))
                total = data.get("total", len(users))
            elif isinstance(data, list):
                users = data
                total = len(data)
        elif resp is None:
            error = "Could not load users — API unavailable"

    return templates.TemplateResponse(request, "users/list.html", {
        "users": users,
        "q": q,
        "page": page,
        "total": total,
        "status_filter": status,
        "has_next": len(users) == 30,
        "error": error,
        "admin_name": get_admin_name(request),
        "active_nav": "users",
    })


@admin_app.get("/users/{user_id}", response_class=HTMLResponse)
async def user_detail(user_id: str, request: Request, token: str = Depends(get_admin_token)):
    user = None
    subscription = None
    stats = None
    error = None

    async with _make_client(token) as client:
        user_resp = await _safe_get(client, f"/admin/users/{user_id}")
        if user_resp:
            user = user_resp.get("data", user_resp) if isinstance(user_resp, dict) else user_resp
        else:
            error = "User not found or API unavailable"

        sub_resp = await _safe_get(client, f"/admin/users/{user_id}/subscription")
        if sub_resp:
            subscription = sub_resp.get("data", sub_resp) if isinstance(sub_resp, dict) else sub_resp

        stats_resp = await _safe_get(client, f"/admin/users/{user_id}/stats")
        if stats_resp:
            stats = stats_resp.get("data", stats_resp) if isinstance(stats_resp, dict) else stats_resp

    success = request.query_params.get("success")
    return templates.TemplateResponse(request, "users/detail.html", {
        "user": user,
        "subscription": subscription,
        "stats": stats,
        "error": error,
        "success": success,
        "admin_name": get_admin_name(request),
        "active_nav": "users",
    })


@admin_app.post("/users/{user_id}/suspend")
async def suspend_user(user_id: str, request: Request, token: str = Depends(get_admin_token)):
    async with _make_client(token) as client:
        try:
            await _api(client, "post", f"/admin/users/{user_id}/suspend",
                       json={}, headers={"Content-Type": "application/json"})
        except (AdminApiError, httpx.HTTPError):
            pass
    return RedirectResponse(f"/admin/users/{user_id}?success=suspended", status_code=302)


@admin_app.post("/users/{user_id}/activate")
async def activate_user(user_id: str, request: Request, token: str = Depends(get_admin_token)):
    async with _make_client(token) as client:
        try:
            await _api(client, "post", f"/admin/users/{user_id}/activate",
                       json={}, headers={"Content-Type": "application/json"})
        except (AdminApiError, httpx.HTTPError):
            pass
    return RedirectResponse(f"/admin/users/{user_id}?success=activated", status_code=302)


# ── Subscriptions ─────────────────────────────────────────────────────────────

@admin_app.get("/subscriptions", response_class=HTMLResponse)
async def subscriptions_list(request: Request, token: str = Depends(get_admin_token),
                              plan: str = "all", page: int = 1):
    subscriptions: list = []
    total = 0
    plans_list: list = []
    error = None

    async with _make_client(token) as client:
        params: dict = {"page": page, "limit": 30}
        if plan != "all":
            params["plan"] = plan

        subs_resp = await _safe_get(client, "/admin/subscriptions", params=params)
        if subs_resp:
            data = subs_resp.get("data", subs_resp) if isinstance(subs_resp, dict) else {}
            if isinstance(data, dict):
                subscriptions = data.get("subscriptions", data.get("items", []))
                total = data.get("total", len(subscriptions))
            elif isinstance(data, list):
                subscriptions = data

        plans_resp = await _safe_get(client, "/subscriptions/plans")
        if plans_resp:
            pdata = plans_resp.get("data", plans_resp) if isinstance(plans_resp, dict) else []
            plans_list = pdata if isinstance(pdata, list) else []

    return templates.TemplateResponse(request, "subscriptions/index.html", {
        "subscriptions": subscriptions,
        "total": total,
        "plans": plans_list,
        "plan_filter": plan,
        "page": page,
        "has_next": len(subscriptions) == 30,
        "error": error,
        "admin_name": get_admin_name(request),
        "active_nav": "subscriptions",
    })


@admin_app.get("/subscriptions/plans", response_class=HTMLResponse)
async def subscription_plans(request: Request, token: str = Depends(get_admin_token)):
    plans: list = []

    async with _make_client(token) as client:
        resp = await _safe_get(client, "/subscriptions/plans")
        if resp:
            data = resp.get("data", resp) if isinstance(resp, dict) else resp
            plans = data if isinstance(data, list) else []

    return templates.TemplateResponse(request, "subscriptions/plans.html", {
        "plans": plans,
        "admin_name": get_admin_name(request),
        "active_nav": "subscriptions",
    })


# ── Support ───────────────────────────────────────────────────────────────────

@admin_app.get("/support/tickets", response_class=HTMLResponse)
async def support_tickets(request: Request, token: str = Depends(get_admin_token),
                           status_filter: str = "open", page: int = 1):
    tickets: list = []
    error = None

    async with _make_client(token) as client:
        params: dict = {"page": page, "limit": 30}
        if status_filter != "all":
            params["status"] = status_filter

        resp = await _safe_get(client, "/admin/support/tickets", params=params)
        if resp:
            data = resp.get("data", {}) if isinstance(resp, dict) else {}
            if isinstance(data, dict):
                tickets = data.get("tickets", data.get("items", []))
            elif isinstance(data, list):
                tickets = data
        elif resp is None:
            error = "Could not load tickets — API unavailable"

    return templates.TemplateResponse(request, "support/tickets.html", {
        "tickets": tickets,
        "status_filter": status_filter,
        "page": page,
        "error": error,
        "admin_name": get_admin_name(request),
        "active_nav": "support",
    })


@admin_app.get("/support/tickets/{ticket_id}", response_class=HTMLResponse)
async def ticket_detail(ticket_id: str, request: Request, token: str = Depends(get_admin_token)):
    ticket = None
    messages: list = []
    error = None

    async with _make_client(token) as client:
        resp = await _safe_get(client, f"/admin/support/tickets/{ticket_id}")
        if resp:
            data = resp.get("data", {}) if isinstance(resp, dict) else {}
            ticket = data.get("ticket", data) if isinstance(data, dict) else data
            messages = data.get("messages", []) if isinstance(data, dict) else []
        else:
            error = "Ticket not found or API unavailable"

    return templates.TemplateResponse(request, "support/ticket_detail.html", {
        "ticket": ticket,
        "messages": messages,
        "error": error,
        "admin_name": get_admin_name(request),
        "active_nav": "support",
    })


@admin_app.post("/support/tickets/{ticket_id}/reply")
async def support_reply(ticket_id: str, request: Request,
                        content: str = Form(...), token: str = Depends(get_admin_token)):
    async with _make_client(token) as client:
        try:
            await _api(client, "post", f"/admin/support/tickets/{ticket_id}/messages",
                       json={"message": content}, headers={"Content-Type": "application/json"})
        except (AdminApiError, httpx.HTTPError):
            pass
    return RedirectResponse(f"/admin/support/tickets/{ticket_id}", status_code=302)


# ── Notifications ─────────────────────────────────────────────────────────────

@admin_app.get("/notifications", response_class=HTMLResponse)
async def notifications_page(request: Request, token: str = Depends(get_admin_token)):
    success = request.query_params.get("success")
    return templates.TemplateResponse(request, "notifications/send.html", {
        "success": success,
        "admin_name": get_admin_name(request),
        "active_nav": "notifications",
    })


@admin_app.post("/notifications/send")
async def send_notification(request: Request,
                            target: str = Form("all"),
                            title: str = Form(...),
                            body: str = Form(...),
                            token: str = Depends(get_admin_token)):
    async with _make_client(token) as client:
        try:
            await _api(client, "post", "/admin/notifications/send",
                       json={"target": target, "title": title, "body": body},
                       headers={"Content-Type": "application/json"})
        except (AdminApiError, httpx.HTTPError):
            pass
    return RedirectResponse("/admin/notifications?success=1", status_code=302)


# ── Content: Words ────────────────────────────────────────────────────────────

@admin_app.get("/content/words", response_class=HTMLResponse)
async def content_words(request: Request, token: str = Depends(get_admin_token),
                        language_id: int = 1, q: str = "", page: int = 1):
    words: list = []

    async with _make_client(token) as client:
        params = {"language_id": language_id, "page": page, "limit": 30}
        if q:
            params["q"] = q
        resp = await _safe_get(client, "/admin/words", params=params)
        if resp:
            data = resp.get("data", resp) if isinstance(resp, dict) else resp
            words = data.get("words", data.get("items", data)) if isinstance(data, dict) else (data if isinstance(data, list) else [])

    return templates.TemplateResponse(request, "content/words.html", {
        "words": words,
        "language_id": language_id,
        "q": q,
        "page": page,
        "admin_name": get_admin_name(request),
        "active_nav": "content",
    })


@admin_app.get("/content/daily-lessons", response_class=HTMLResponse)
async def content_lessons(request: Request, token: str = Depends(get_admin_token),
                          language_id: int = 1, page: int = 1):
    lessons: list = []

    async with _make_client(token) as client:
        params = {"language_id": language_id, "page": page, "limit": 30}
        resp = await _safe_get(client, "/admin/lessons", params=params)
        if resp:
            data = resp.get("data", resp) if isinstance(resp, dict) else resp
            lessons = data.get("lessons", data.get("items", [])) if isinstance(data, dict) else []

    return templates.TemplateResponse(request, "content/daily_lessons.html", {
        "lessons": lessons,
        "language_id": language_id,
        "page": page,
        "admin_name": get_admin_name(request),
        "active_nav": "content",
    })


# ── Settings ──────────────────────────────────────────────────────────────────

@admin_app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, token: str = Depends(get_admin_token)):
    return templates.TemplateResponse(request, "settings/index.html", {
        "admin_name": get_admin_name(request),
        "active_nav": "settings",
        "api_base_url": settings.API_BASE_URL,
    })
