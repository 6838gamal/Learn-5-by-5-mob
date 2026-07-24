from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.models.support import SupportTicket, SupportMessage

router = APIRouter()


class CreateTicketRequest(BaseModel):
    subject: str
    category: str | None = None
    description: str


class SendMessageRequest(BaseModel):
    content: str


def ok(data):
    return {"success": True, "data": data, "message": None}


@router.post("/tickets", status_code=201)
async def create_ticket(
    body: CreateTicketRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ticket = SupportTicket(
        user_id=current_user.id,
        subject=body.subject,
        category=body.category,
    )
    db.add(ticket)
    await db.flush()
    await db.refresh(ticket)

    msg = SupportMessage(
        ticket_id=ticket.id,
        sender_type="user",
        sender_id=current_user.id,
        content=body.description,
    )
    db.add(msg)
    await db.flush()

    return ok({"ticket_id": ticket.id, "status": ticket.status})


@router.get("/tickets")
async def list_tickets(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SupportTicket)
        .where(SupportTicket.user_id == current_user.id)
        .order_by(SupportTicket.created_at.desc())
    )
    tickets = result.scalars().all()
    return ok({"tickets": [{"id": t.id, "subject": t.subject, "status": t.status, "created_at": t.created_at.isoformat()} for t in tickets]})


@router.get("/tickets/{ticket_id}")
async def get_ticket(
    ticket_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SupportTicket).where(
            SupportTicket.id == ticket_id, SupportTicket.user_id == current_user.id
        )
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise NotFoundError("Ticket")

    msgs_result = await db.execute(
        select(SupportMessage).where(SupportMessage.ticket_id == ticket_id).order_by(SupportMessage.created_at)
    )
    messages = msgs_result.scalars().all()

    return ok({
        "ticket": {"id": ticket.id, "subject": ticket.subject, "status": ticket.status, "category": ticket.category},
        "messages": [{"id": m.id, "sender_type": m.sender_type, "content": m.content, "created_at": m.created_at.isoformat()} for m in messages],
    })


@router.post("/tickets/{ticket_id}/messages")
async def send_message(
    ticket_id: str,
    body: SendMessageRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SupportTicket).where(SupportTicket.id == ticket_id, SupportTicket.user_id == current_user.id)
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise NotFoundError("Ticket")

    msg = SupportMessage(
        ticket_id=ticket_id,
        sender_type="user",
        sender_id=current_user.id,
        content=body.content,
    )
    db.add(msg)
    await db.flush()
    await db.refresh(msg)
    return ok({"message_id": msg.id, "created_at": msg.created_at.isoformat()})
