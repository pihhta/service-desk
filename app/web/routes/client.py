from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.db.session import get_db
from app.models.client import Client
from app.models.product import Product
from app.models.ticket import Ticket
from app.models.user import User
from app.web.templates import templates

router = APIRouter(tags=["client"])


async def _get_client_for_user(db: AsyncSession, user: User) -> Client | None:
    result = await db.execute(select(Client).where(Client.email == user.email))
    return result.scalar_one_or_none()


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("client")),
):
    client = await _get_client_for_user(db, user)
    if not client:
        return templates.TemplateResponse(
            "client/dashboard.html",
            {
                "request": request,
                "user": user,
                "stats": {"open": 0, "in_progress": 0, "total": 0},
                "recent_tickets": [],
            },
        )
    result = await db.execute(
        select(Ticket).where(Ticket.client_id == client.id)
    )
    tickets = result.scalars().all()

    stats = {
        "open": sum(1 for t in tickets if t.status == "new"),
        "in_progress": sum(1 for t in tickets if t.status == "in_progress"),
        "total": len(tickets),
    }
    recent = sorted(tickets, key=lambda t: t.created_at, reverse=True)[:5]

    return templates.TemplateResponse(
        "client/dashboard.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "recent_tickets": recent,
        },
    )


@router.get("/tickets", response_class=HTMLResponse)
async def tickets(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("client")),
):
    client = await _get_client_for_user(db, user)
    if not client:
        return templates.TemplateResponse(
            "client/tickets.html",
            {"request": request, "user": user, "tickets": []},
        )
    result = await db.execute(
        select(Ticket)
        .where(Ticket.client_id == client.id)
        .order_by(Ticket.created_at.desc())
    )
    return templates.TemplateResponse(
        "client/tickets.html",
        {"request": request, "user": user, "tickets": result.scalars().all()},
    )


@router.get("/tickets/new", response_class=HTMLResponse)
async def ticket_create_form(
    request: Request,
    user: User = Depends(require_role("client")),
):
    return templates.TemplateResponse(
        "client/ticket_new.html",
        {"request": request, "user": user},
    )


@router.post("/tickets/new")
async def ticket_create(
    request: Request,
    subject: str = Form(...),
    description: str = Form(...),
    product_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("client")),
):
    client = await _get_client_for_user(db, user)
    if not client:
        return RedirectResponse(url="/client", status_code=303)

    ticket = Ticket(
        subject=subject,
        description=description,
        status="new",
        priority="medium",
        client_id=client.id,
        product_id=product_id,
        author_id=user.id,
    )
    db.add(ticket)
    await db.flush()
    await db.commit()
    return RedirectResponse(url="/client/tickets", status_code=303)


@router.get("/tickets/{ticket_id}", response_class=HTMLResponse)
async def ticket_detail(
    ticket_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("client")),
):
    client = await _get_client_for_user(db, user)
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket or not client or ticket.client_id != client.id:
        return RedirectResponse(url="/client/tickets", status_code=303)
    return templates.TemplateResponse(
        "client/ticket_detail.html",
        {"request": request, "user": user, "ticket": ticket},
    )