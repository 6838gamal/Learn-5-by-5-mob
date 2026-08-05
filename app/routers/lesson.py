"""Lesson router — 11-step daily lesson flow."""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def lesson_page(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.get("/lessons/today")
        lesson = resp.get("data", resp)
    except ApiError as e:
        lesson = None
        error = e.detail
    else:
        error = None
    finally:
        await client.aclose()

    return templates.TemplateResponse(request, "lesson.html", {
        "lesson": lesson,
        "error": error,
    })


@router.post("/progress")
async def save_progress(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    body = await request.json()
    try:
        resp = await client.post("/lessons/progress", json=body)
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()
