"""Home / dashboard router."""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def home_page(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    lesson_data = streak_data = review_count = user_data = None
    errors = []

    try:
        resp = await client.get("/lessons/today")
        lesson_data = resp.get("data", resp)
    except ApiError as e:
        errors.append(f"Lesson: {e.detail}")

    try:
        resp = await client.get("/lessons/streak")
        streak_data = resp.get("data", resp)
    except ApiError as e:
        errors.append(f"Streak: {e.detail}")

    try:
        resp = await client.get("/review/count")
        review_count = resp.get("data", {}).get("count", 0) if isinstance(resp, dict) else 0
    except ApiError:
        review_count = 0

    try:
        resp = await client.get("/auth/me")
        user_data = resp.get("data", resp)
    except ApiError:
        pass

    await client.aclose()

    return templates.TemplateResponse("home.html", {
        "request": request,
        "lesson": lesson_data,
        "streak": streak_data,
        "review_count": review_count,
        "user": user_data,
        "errors": errors,
    })
