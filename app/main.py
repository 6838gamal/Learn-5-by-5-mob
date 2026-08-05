"""Learn 5 by 5 — FastAPI web app entry point."""

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.routers import auth, onboarding, home, lesson, review, quiz, ai_chat, profile, subscription, support, notifications
settings = get_settings()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE_NAME,
    same_site="lax",
    https_only=False,
    max_age=60 * 60 * 24 * 30,  # 30 days
)

# ── Static files ──────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router,         prefix="/auth",          tags=["auth"])
app.include_router(onboarding.router,   prefix="/onboarding",    tags=["onboarding"])
app.include_router(home.router,         prefix="/home",          tags=["home"])
app.include_router(lesson.router,       prefix="/lesson",        tags=["lesson"])
app.include_router(review.router,       prefix="/review",        tags=["review"])
app.include_router(quiz.router,         prefix="/quiz",          tags=["quiz"])
app.include_router(ai_chat.router,      prefix="/ai-chat",       tags=["ai_chat"])
app.include_router(profile.router,      prefix="/profile",       tags=["profile"])
app.include_router(subscription.router, prefix="/subscription",  tags=["subscription"])
app.include_router(support.router,      prefix="/support",       tags=["support"])
app.include_router(notifications.router,prefix="/notifications", tags=["notifications"])


# ── Splash screen ─────────────────────────────────────────────────────────────
templates = Jinja2Templates(directory="app/templates")

@app.get("/splash", response_class=HTMLResponse)
async def splash(request: Request):
    if request.session.get("access_token"):
        redirect_url = "/home"
    else:
        redirect_url = "/auth/login"
    return templates.TemplateResponse(request, "splash.html", {
        "redirect_url": redirect_url,
    })


# ── Root redirect ─────────────────────────────────────────────────────────────
@app.get("/")
async def root(request: Request):
    return RedirectResponse("/splash")
