from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.db.session import get_db
from app.models.product import Product
from app.models.ticket import Ticket
from app.models.user import User
from app.web.templates import templates

router = APIRouter(tags=["agent"])

STATUSES = [
    {"value": "new", "label": "Новый"},
    {"value": "in_progress", "label": "В работе"},
    {"value": "waiting", "label": "Ожидает ответа"},
    {"value": "resolved", "label": "Решён"},
    {"value": "closed", "label": "Закрыт"},
]

STATUS_CODES = [s["value"] for s in STATUSES]


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("agent", "manager")),
):
    my_count = await db.scalar(
        select(func.count()).select_from(Ticket).where(
            Ticket.assignee_id == user.id,
            Ticket.status.in_(["new", "in_progress", "waiting"]),
        )
    )
    unassigned_count = await db.scalar(
        select(func.count()).select_from(Ticket).where(
            Ticket.assignee_id.is_(None),
            Ticket.status == "new",
        )
    )
    overdue = 0
    resolved_today = 0

    result = await db.execute(
        select(Ticket)
        .where(
            Ticket.assignee_id == user.id,
            Ticket.status.in_(["new", "in_progress", "waiting"]),
        )
        .order_by(Ticket.created_at.desc())
        .limit(5)
    )
    my_tickets = result.scalars().all()

    result = await db.execute(
        select(Ticket)
        .where(
            Ticket.assignee_id.is_(None),
            Ticket.status == "new",
        )
        .order_by(Ticket.created_at.desc())
        .limit(5)
    )
    unassigned_tickets = result.scalars().all()

    return templates.TemplateResponse(
        "agent/dashboard.html",
        {
            "request": request,
            "user": user,
            "stats": {
                "my_open": my_count or 0,
                "unassigned": unassigned_count or 0,
                "overdue": overdue,
                "resolved_today": resolved_today,
            },
            "my_tickets": my_tickets,
            "unassigned_tickets": unassigned_tickets,
        },
    )


@router.get("/tickets", response_class=HTMLResponse)
async def tickets(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("agent", "manager")),
):
    result = await db.execute(
        select(Ticket).order_by(Ticket.created_at.desc())
    )
    tickets_list = result.scalars().all()

    products_result = await db.execute(select(Product).order_by(Product.name))
    products_list = products_result.scalars().all()

    return templates.TemplateResponse(
        "agent/tickets.html",
        {
            "request": request,
            "user": user,
            "tickets": tickets_list,
            "products": products_list,
        },
    )


@router.get("/tickets/{ticket_id}", response_class=HTMLResponse)
async def ticket_detail(
    request: Request,
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("agent", "manager")),
):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        return RedirectResponse(url="/agent/tickets", status_code=303)
    return templates.TemplateResponse(
        "agent/ticket_detail.html",
        {
            "request": request,
            "user": user,
            "ticket": ticket,
            "statuses": STATUSES,
        },
    )


@router.post("/tickets/{ticket_id}/update")
async def update_ticket(
    ticket_id: int,
    status: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("agent", "manager")),
):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        return RedirectResponse(url="/agent/tickets", status_code=303)

    if status in STATUS_CODES:
        ticket.status = status
    if ticket.assignee_id is None:
        ticket.assignee_id = user.id

    return RedirectResponse(
        url=f"/agent/tickets/{ticket_id}", status_code=303
    )


@router.post("/tickets/{ticket_id}/take")
async def take_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("agent")),
):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if ticket and ticket.assignee_id is None:
        ticket.assignee_id = user.id
        ticket.status = "in_progress"
    return RedirectResponse(
        url=f"/agent/tickets/{ticket_id}", status_code=303
    )