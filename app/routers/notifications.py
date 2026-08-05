"""Notifications router."""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def notifications_page(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.get("/notifications/")
        # Response shape: {"success": true, "data": {"notifications": [...]}}
        data = resp.get("data", {}) if isinstance(resp, dict) else {}
        items = data.get("notifications", []) if isinstance(data, dict) else []
    except ApiError as e:
        items = []
        error = e.detail
    else:
        error = None
    finally:
        await client.aclose()

    return templates.TemplateResponse(request, "notifications.html", {
        "notifications": items,
        "error": error,
    })


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.patch(f"/notifications/{notification_id}/read")
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()


@router.post("/read-all")
async def mark_all_read(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.patch("/notifications/read-all")
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()
