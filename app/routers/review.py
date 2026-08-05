"""Review router — spaced-repetition flashcard session."""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def review_page(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.get("/review/due")
        words = resp.get("data", resp) if isinstance(resp, dict) else resp
    except ApiError as e:
        words = []
        error = e.detail
    else:
        error = None
    finally:
        await client.aclose()

    return templates.TemplateResponse("review.html", {
        "request": request,
        "words": words,
        "error": error,
    })


@router.post("/submit")
async def submit_review(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    body = await request.json()
    try:
        resp = await client.post("/review/submit", json=body)
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()
