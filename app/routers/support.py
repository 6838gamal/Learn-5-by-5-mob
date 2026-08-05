"""Support tickets router."""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.api_client import ApiClient, ApiError
from app.dependencies import get_api_client, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def tickets_list(
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.get("/support/tickets")
        tickets = resp.get("data", resp) if isinstance(resp, dict) else resp
    except ApiError as e:
        tickets = []
        error = e.detail
    else:
        error = None
    finally:
        await client.aclose()

    return templates.TemplateResponse("support/tickets.html", {
        "request": request,
        "tickets": tickets,
        "error": error,
    })


@router.post("", response_class=HTMLResponse)
async def create_ticket(
    request: Request,
    subject: str = Form(...),
    message: str = Form(...),
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.post("/support/tickets", json={"subject": subject, "message": message})
        ticket_id = resp.get("data", {}).get("id") if isinstance(resp, dict) else None
        if ticket_id:
            return RedirectResponse(f"/support/{ticket_id}", status_code=303)
        return RedirectResponse("/support", status_code=303)
    except ApiError as e:
        return templates.TemplateResponse("support/tickets.html", {
            "request": request,
            "tickets": [],
            "error": e.detail,
        }, status_code=400)
    finally:
        await client.aclose()


@router.get("/{ticket_id}", response_class=HTMLResponse)
async def ticket_detail(
    ticket_id: str,
    request: Request,
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        resp = await client.get(f"/support/tickets/{ticket_id}")
        ticket = resp.get("data", resp)
    except ApiError as e:
        ticket = None
        error = e.detail
    else:
        error = None
    finally:
        await client.aclose()

    return templates.TemplateResponse("support/ticket_detail.html", {
        "request": request,
        "ticket": ticket,
        "error": error,
    })


@router.post("/{ticket_id}/messages", response_class=HTMLResponse)
async def add_message(
    ticket_id: str,
    request: Request,
    message: str = Form(...),
    client: ApiClient = Depends(get_api_client),
    _auth=Depends(require_auth),
):
    try:
        await client.post(f"/support/tickets/{ticket_id}/messages", json={"message": message})
        return RedirectResponse(f"/support/{ticket_id}", status_code=303)
    except ApiError as e:
        return RedirectResponse(f"/support/{ticket_id}?error={e.detail}", status_code=303)
    finally:
        await client.aclose()
