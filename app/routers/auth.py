"""Auth router — login, register, forgot password, logout."""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client
from app.config import get_settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


# ── Login ─────────────────────────────────────────────────────────────────────
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("access_token"):
        return RedirectResponse("/home")
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "google_client_id": settings.GOOGLE_WEB_CLIENT_ID,
        "error": None,
    })


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    client: ApiClient = Depends(get_api_client),
):
    try:
        data = await client.post("/auth/login", json={"email": email, "password": password})
        tokens = data.get("data", data)
        request.session["access_token"] = tokens["access_token"]
        request.session["refresh_token"] = tokens.get("refresh_token", "")
        return RedirectResponse("/home", status_code=303)
    except ApiError as e:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "google_client_id": settings.GOOGLE_WEB_CLIENT_ID,
            "error": e.detail,
        }, status_code=400)
    finally:
        await client.aclose()


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
        return RedirectResponse("/home", status_code=303)
    except ApiError as e:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "google_client_id": settings.GOOGLE_WEB_CLIENT_ID,
            "error": e.detail,
        }, status_code=400)
    finally:
        await client.aclose()


# ── Register ──────────────────────────────────────────────────────────────────
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request, "error": None})


@router.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    client: ApiClient = Depends(get_api_client),
):
    try:
        data = await client.post("/auth/register", json={"full_name": full_name, "email": email, "password": password})
        tokens = data.get("data", data)
        request.session["access_token"] = tokens["access_token"]
        request.session["refresh_token"] = tokens.get("refresh_token", "")
        return RedirectResponse("/onboarding", status_code=303)
    except ApiError as e:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": e.detail,
        }, status_code=400)
    finally:
        await client.aclose()


# ── Forgot password ───────────────────────────────────────────────────────────
@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_page(request: Request):
    return templates.TemplateResponse("auth/forgot_password.html", {
        "request": request,
        "sent": False,
        "error": None,
    })


@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_submit(
    request: Request,
    email: str = Form(...),
    client: ApiClient = Depends(get_api_client),
):
    try:
        await client.post("/auth/forgot-password", json={"email": email})
        return templates.TemplateResponse("auth/forgot_password.html", {
            "request": request,
            "sent": True,
            "error": None,
        })
    except ApiError as e:
        return templates.TemplateResponse("auth/forgot_password.html", {
            "request": request,
            "sent": False,
            "error": e.detail,
        }, status_code=400)
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
