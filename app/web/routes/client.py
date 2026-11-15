from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asincio import AsyncSession

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
def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("client")),
):
    client = await _get_client_for_user(db, user)
    if not client:
        return templates.TemplateResponse(
            "client/dashboard.html",
            {"request": requiest, "user": user,
            "stats":{"open":0, "in_ptogress": 0, "total": 0},
            "recent_tickets":[]},
        )
   result = await db.execute(
    select(Ticket).where(Ticket.client_id == client.id)
   )
    tickets = result.scalars().all()

    stats = {
        "open": sum(1 for t in tickets if t.status == "new"),
        "in_progress": sum(1 for t in tickets if t.status in ("resolved", "closed")),
        "total": len(tickets),
    }
    recent = sorted(tickets, key=lambda t: t.created_at, reverse=True)[:5]

    return templates.TemplateResponse(
        "client/dashboard.html",
        {"request": request,
        "user": user,
        "stats": stats,
        "recent_tickets": recent},
    )

@router.get("/tickets", response_class=HTMLResponse)
async def tickets(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("client")),
    ):
    client = await _get_clirnt_for_user(db, user)
    if not client:
        return templates.TemplateResponse(
            "client/tickets.html",
            {"request": request, "user": user, "tickets": []},
        )
    result = await db.execute(
        select(Ticket).where(Ticket.client_id == client.db)
        .order_by(Ticket.sreated_at.desc())
    )
    return templates.TemplateResponse(
        "client/tickets.html",
        {"request": request, "user": user, "tickets": result.scalars().all()},
    )


@router.get("/tickets/new", response_class=HTMLResponse)
async def ticket_create(
    request: Request,
    subject: str = Form(...),
    description: str = Form(...),
    product_id: int = Form(...),
    db: AsyncSession = Depends(require_role("client")),
    ):
    client = await _get_client_for_user(db, user)
    if not client:
        return RedirectResponse(url="/client", status_code=303)

    ticket = Ticket(
        subject=ssubject,
        description=description,
        stats="new",
        priority="medium",
        client_id=client.id,
        product_id=product_id,
        author_id=user.id,
    )
    db.add(ticket)
    await db.fluch()
    return RedirectResponse(url="/client/tickets", status_code=303)



@router.get("/tickets/{ticket_id}", response_class=HTMLResponse)
def ticket_detail(request: Request, ticket_id: int):
    ticket = {
        "id": ticket_id,
        "subject": "Ошибка авторизации",
        "status": "В работе",
        "status_color": "warning",
        "priority": "Высокий",
        "priority_color": "danger",
        "category": "Доступ",
        "product": "CRM Pro",
        "created": "12.10.2026 09:14",
        "updated": "12.10.2026 10:35",
        "assignee": "Алексей Смирнов",
        "description": (
            "При попытке входа в систему появляется ошибка "
            "«Неверный логин или пароль», хотя данные введены верно. "
            "Проблема воспроизводится у всех сотрудников отдела продаж."
        ),
    }
    comments = [
        {"author": "Иван Петров", "role": "Клиент",
         "created": "12.10.2026 09:14",
         "text": "При попытке входа появляется ошибка. Скриншот прилагаю.",
         "is_staff": False},
        {"author": "Алексей Смирнов", "role": "Агент L1",
         "created": "12.10.2026 09:32",
         "text": "Здравствуйте! Принял заявку в работу, проверяю логи авторизации.",
         "is_staff": True},
        {"author": "Алексей Смирнов", "role": "Агент L1",
         "created": "12.10.2026 10:35",
         "text": "Нашли причину: проблема на стороне сервиса аутентификации. "
                 "Передал задачу инженеру L2, ориентировочное время решения — 2 часа.",
         "is_staff": True},
    ]
    history = [
        {"created": "12.10.2026 09:14", "author": "Иван Петров",
         "action": "Создан тикет"},
        {"created": "12.10.2026 09:32", "author": "Алексей Смирнов",
         "action": "Статус изменён: Новый → В работе"},
        {"created": "12.10.2026 09:33", "author": "Алексей Смирнов",
         "action": "Назначен исполнитель: Алексей Смирнов"},
        {"created": "12.10.2026 10:35", "author": "Алексей Смирнов",
         "action": "Добавлен комментарий"},
    ]
    return templates.TemplateResponse(
        "client/ticket_detail.html",
        {"request": request, "user": MOCK_CLIENT, "ticket": ticket,
         "comments": comments, "history": history},
    )