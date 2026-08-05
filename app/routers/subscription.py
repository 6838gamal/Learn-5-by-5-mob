"""Subscription router — plans, checkout, current subscription."""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def subscription_page(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    plans = current = None
    try:
        resp = await client.get("/subscriptions/plans")
        plans = resp.get("data", resp) if isinstance(resp, dict) else resp
    except ApiError:
        plans = []

    try:
        resp = await client.get("/subscriptions/current")
        current = resp.get("data", resp)
    except ApiError:
        current = None

    await client.aclose()

    return templates.TemplateResponse(request, "profile/subscription.html", {
        "plans": plans,
        "current": current,
        "error": request.query_params.get("error"),
        "success": request.query_params.get("success"),
    })


@router.post("/checkout")
async def checkout(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    body = await request.json()
    try:
        resp = await client.post("/subscriptions/checkout", json=body)
        return JSONResponse(resp)
    except ApiError as e:
        return JSONResponse({"error": e.detail}, status_code=e.status_code)
    finally:
        await client.aclose()


@router.post("/cancel")
async def cancel_subscription(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.post("/subscriptions/cancel", json={})
        return RedirectResponse("/subscription?success=1", status_code=303)
    except ApiError as e:
        return RedirectResponse(f"/subscription?error={e.detail}", status_code=303)
    finally:
        await client.aclose()
