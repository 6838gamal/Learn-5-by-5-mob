"""Onboarding router — target language, UI language, proficiency level."""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def onboarding_page(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        lang_resp = await client.get("/languages/")
        languages = lang_resp.get("data", lang_resp) if isinstance(lang_resp, dict) else lang_resp
    except ApiError:
        languages = [
            {"code": "en", "name": "English"},
            {"code": "ar", "name": "Arabic"},
            {"code": "fr", "name": "French"},
            {"code": "es", "name": "Spanish"},
            {"code": "de", "name": "German"},
        ]
    finally:
        await client.aclose()

    return templates.TemplateResponse("onboarding.html", {
        "request": request,
        "languages": languages,
        "error": None,
    })


@router.post("", response_class=HTMLResponse)
async def onboarding_submit(
    request: Request,
    target_language: str = Form(...),
    ui_language: str = Form("en"),
    level: str = Form("beginner"),
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        await client.patch("/users/profile", json={
            "target_language": target_language,
            "ui_language": ui_language,
            "level": level,
        })
        request.session["onboarded"] = True
        return RedirectResponse("/home", status_code=303)
    except ApiError as e:
        lang_resp = await client.get("/languages/")
        languages = lang_resp.get("data", lang_resp) if isinstance(lang_resp, dict) else lang_resp
        return templates.TemplateResponse("onboarding.html", {
            "request": request,
            "languages": languages,
            "error": e.detail,
        }, status_code=400)
    finally:
        await client.aclose()
