"""Profile & settings router."""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.get("/auth/me")
        user = resp.get("data", resp)
    except ApiError:
        user = {}
    finally:
        await client.aclose()

    return templates.TemplateResponse("profile/index.html", {
        "request": request,
        "user": user,
        "success": request.query_params.get("success"),
        "error": None,
    })


@router.post("", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    full_name: str = Form(""),
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        await client.patch("/users/profile", json={"full_name": full_name})
        return RedirectResponse("/profile?success=1", status_code=303)
    except ApiError as e:
        user = {}
        return templates.TemplateResponse("profile/index.html", {
            "request": request,
            "user": {"full_name": full_name},
            "success": None,
            "error": e.detail,
        }, status_code=400)
    finally:
        await client.aclose()


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    _auth=Depends(require_auth),
):
    theme = request.session.get("theme", "light")
    locale = request.session.get("locale", "en")
    return templates.TemplateResponse("profile/settings.html", {
        "request": request,
        "theme": theme,
        "locale": locale,
        "success": request.query_params.get("success"),
    })


@router.post("/settings", response_class=HTMLResponse)
async def save_settings(
    request: Request,
    theme: str = Form("light"),
    locale: str = Form("en"),
    _auth=Depends(require_auth),
):
    request.session["theme"] = theme
    request.session["locale"] = locale
    return RedirectResponse("/profile/settings?success=1", status_code=303)


@router.post("/change-password", response_class=HTMLResponse)
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        await client.patch("/users/password", json={
            "current_password": current_password,
            "new_password": new_password,
        })
        return RedirectResponse("/profile?success=1", status_code=303)
    except ApiError as e:
        return templates.TemplateResponse("profile/index.html", {
            "request": request,
            "user": {},
            "success": None,
            "error": e.detail,
        }, status_code=400)
    finally:
        await client.aclose()
