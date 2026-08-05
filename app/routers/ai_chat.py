"""AI Chat router — voice conversation with AI tutor (proxied to backend)."""

from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def ai_chat_page(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    # Pre-fetch user's target language so the template can start a conversation
    try:
        profile_resp = await client.get("/auth/me")
        profile = profile_resp.get("data", {}) if isinstance(profile_resp, dict) else {}
        language_id = profile.get("target_language_id", "")
    except ApiError:
        language_id = ""
    finally:
        await client.aclose()

    return templates.TemplateResponse(request, "ai_chat.html", {
        "language_id": language_id,
    })


@router.post("/start")
async def start_conversation(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    """Start an AI conversation. Backend expects multipart/form-data with language_id."""
    body = await request.json()
    language_id = body.get("language_id", "")
    scenario_id = body.get("scenario_id")

    form_data: dict = {"language_id": str(language_id)}
    if scenario_id:
        form_data["scenario_id"] = str(scenario_id)

    try:
        resp = await client.post_form("/ai/conversation/start", data=form_data)
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()


@router.post("/{conversation_id}/message")
async def send_message(
    conversation_id: str,
    request: Request,
    audio: UploadFile = File(...),
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    """Forward audio recording to the backend AI endpoint."""
    audio_bytes = await audio.read()
    try:
        resp = await client.post_form(
            f"/ai/conversation/{conversation_id}/message",
            files={"audio": (audio.filename or "recording.webm", audio_bytes, audio.content_type or "audio/webm")},
        )
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()


@router.post("/{conversation_id}/end")
async def end_conversation(
    conversation_id: str,
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.post(f"/ai/conversation/{conversation_id}/end", json={})
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()
