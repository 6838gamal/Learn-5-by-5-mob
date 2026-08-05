"""Quiz router — knowledge assessment."""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def quiz_page(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.post("/quiz/start", json={})
        quiz = resp.get("data", resp)
    except ApiError as e:
        quiz = None
        error = e.detail
    else:
        error = None
    finally:
        await client.aclose()

    return templates.TemplateResponse("quiz.html", {
        "request": request,
        "quiz": quiz,
        "error": error,
    })


@router.post("/{quiz_id}/answer")
async def answer_question(
    quiz_id: str,
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    body = await request.json()
    try:
        resp = await client.post(f"/quiz/{quiz_id}/answer", json=body)
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()


@router.post("/{quiz_id}/complete")
async def complete_quiz(
    quiz_id: str,
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.post(f"/quiz/{quiz_id}/complete", json={})
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()
