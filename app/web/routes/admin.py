from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.db.session import get_db
from app.models.client import Client
from app.models.product import Product
from app.models.ticket import Ticket
from app.models.user import User
from app.web.templates import templates

router = APIRouter(tags=["admin"])


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "manager")),
):
    clients_count = await db.scalar(select(func.count()).select_from(Client))
    products_count = await db.scalar(select(func.count()).select_from(Product))
    agents_count = await db.scalar(
        select(func.count()).select_from(User).where(User.role == "agent")
    )
    open_tickets = await db.scalar(
        select(func.count()).select_from(Ticket).where(
            Ticket.status.in_(["new", "in_progress", "waiting"])
        )
    )
    result = await db.execute(
        select(Ticket).order_by(Ticket.created_at.desc()).limit(5)
    )
    recent_tickets = result.scalars().all()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": user,
            "stats": {
                "clients": clients_count or 0,
                "products": products_count or 0,
                "agents": agents_count or 0,
                "open_tickets": open_tickets or 0,
            },
            "recent_tickets": recent_tickets,
        },
    )


@router.get("/users", response_class=HTMLResponse)
async def users(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    result = await db.execute(select(User).order_by(User.id))
    users_list = result.scalars().all()
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "user": user, "users": users_list},
    )


@router.get("/clients", response_class=HTMLResponse)
async def clients(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "manager")),
):
    result = await db.execute(select(Client).order_by(Client.name))
    clients_list = result.scalars().all()
    return templates.TemplateResponse(
        "admin/clients.html",
        {"request": request, "user": user, "clients": clients_list},
    )


from sqlalchemy import func, select
from app.models.product import Product
from app.models.ticket import Ticket


@router.get("/products", response_class=HTMLResponse)
async def products(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "manager")),
):
    result = await db.execute(select(Product).order_by(Product.name))
    products_list = result.scalars().all()

    # Уникальные клиенты на продукт
    clients_result = await db.execute(
        select(Ticket.product_id, func.count(func.distinct(Ticket.client_id)))
        .where(Ticket.product_id.isnot(None))
        .group_by(Ticket.product_id)
    )
    clients_by_product = dict(clients_result.all())

    # Открытые тикеты на продукт
    open_result = await db.execute(
        select(Ticket.product_id, func.count())
        .where(
            Ticket.product_id.isnot(None),
            Ticket.status.in_(["new", "in_progress", "waiting"]),
        )
        .group_by(Ticket.product_id)
    )
    open_by_product = dict(open_result.all())

    return templates.TemplateResponse(
        "admin/products.html",
        {
            "request": request,
            "user": user,
            "products": products_list,
            "clients_by_product": clients_by_product,
            "open_by_product": open_by_product,
        },
    )