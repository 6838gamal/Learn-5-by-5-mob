"""Auth router — Google Sign-In only, logout."""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client
from app.config import get_settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


# ── Login page (Google Sign-In only) ──────────────────────────────────────────
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    if request.session.get("access_token"):
        return RedirectResponse("/home")
    return templates.TemplateResponse(request, "auth/login.html", {
        "google_client_id": settings.GOOGLE_WEB_CLIENT_ID,
        "error": error or None,
    })


# ── Google Sign-In callback ───────────────────────────────────────────────────
@router.post("/google", response_class=HTMLResponse)
async def google_login(
    request: Request,
    id_token: str = Form(...),
    client: ApiClient = Depends(get_api_client),
):
    try:
        data = await client.post("/auth/google", json={"id_token": id_token})
        tokens = data.get("data", data)
        request.session["access_token"] = tokens["access_token"]
        request.session["refresh_token"] = tokens.get("refresh_token", "")
        # First-time users go to onboarding; returning users go to home
        needs_onboarding = tokens.get("needs_onboarding", False)
        destination = "/onboarding" if needs_onboarding else "/home"
        return RedirectResponse(destination, status_code=303)
    except ApiError as e:
        return RedirectResponse(f"/auth/login?error={e.detail}", status_code=303)
    finally:
        await client.aclose()


# ── Logout ────────────────────────────────────────────────────────────────────
@router.post("/logout")
async def logout(request: Request, client: ApiClient = Depends(get_api_client)):
    try:
        await client.post("/auth/logout")
    except Exception:
        pass
    finally:
        await client.aclose()
    request.session.clear()
    return RedirectResponse("/auth/login", status_code=303)
