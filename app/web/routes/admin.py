from fastapi import APIRouter,Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.db.session import get__db
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
    agent_count = await db.scalar(select(func.count()).select_form(User).where(User.role == "agent")
    )
    open_tickets = await db.scalar(select(func.count()).select_form(Ticket).where(Ticket.status.in_(["new", "in_progress", "waiting"])
    )
)
result = await db.execute(
    select(Ticket).order_by(Ticket.created_at.desc()).limit(5)
)
recent_tickets = result.scalass().all()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": user,
            "stats":{
                "clients": clientscount or 0,
                "products": products_count or 0,
                "agents": agents_count or 0,
                "open_tickets": open_tickets or 0,
            },
            "recent_tickets": recent_tickets,
            },
    )


@router.get("/clients", response_class=HTMLResponse)
def clients(request: Request):
    items = [
        {"id": 1, "name": "Ромашка", "contact": "Иван Петров",
         "email": "ivan@romashka.ru", "phone": "+7 900 123-45-67",
         "products": 3, "open_tickets": 4, "active": True},
        {"id": 2, "name": "ТехноСофт", "contact": "Мария Сидорова",
         "email": "m.sidorova@technosoft.ru", "phone": "+7 900 222-33-44",
         "products": 5, "open_tickets": 2, "active": True},
        {"id": 3, "name": "Альфа", "contact": "Олег Кузнецов",
         "email": "o.kuznetsov@alfa.ru", "phone": "+7 900 555-66-77",
         "products": 1, "open_tickets": 0, "active": False},
        {"id": 4, "name": "Бета", "contact": "Анна Морозова",
         "email": "anna@beta.io", "phone": "+7 900 888-99-00",
         "products": 2, "open_tickets": 1, "active": True},
    ]
    return templates.TemplateResponse(
        "admin/clients.html",
        {"request": request, "user": MOCK_ADMIN, "clients": items},
    )


@router.get("/products", response_class=HTMLResponse)
def products(request: Request):
    items = [
                {"id": 1, "name": "CRM Lite", "version": "2.4.1",
         "clients": 5, "open_tickets": 3, "status": "Активен"},
        {"id": 2, "name": "CRM Pro", "version": "3.0.0",
         "clients": 7, "open_tickets": 6, "status": "Активен"},
        {"id": 3, "name": "Billing", "version": "1.8.2",
         "clients": 3, "open_tickets": 1, "status": "Активен"},
        {"id": 4, "name": "Analytics", "version": "0.9.5",
         "clients": 2, "open_tickets": 0, "status": "Бета"},
    ]
    return templates.TemplateResponse(
        "admin/products.html",
        {"request": request, "user": MOCK_ADMIN, "products": items},
    )


@router.get("/users", response_class=HTMLResponse)
def users(request: Request):
    items = [
        {"id": 1, "full_name": "Алексей Смирнов", "email": "a.smirnov@sd.ru",
         "role": "agent", "role_label": "Агент L1", "active": True},
        {"id": 2, "full_name": "Ольга Иванова", "email": "o.ivanova@sd.ru",
         "role": "agent", "role_label": "Агент L2", "active": True},
        {"id": 3, "full_name": "Дмитрий Волков", "email": "d.volkov@sd.ru",
         "role": "manager", "role_label": "Менеджер", "active": True},
        {"id": 4, "full_name": "Екатерина Новикова", "email": "e.novikova@sd.ru",
         "role": "agent", "role_label": "Агент L1", "active": False},
        {"id": 5, "full_name": "Администратор", "email": "admin@example.com",
         "role": "admin", "role_label": "Администратор", "active": True},
    ]
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "user": MOCK_ADMIN, "users": items},
    )