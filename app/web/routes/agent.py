from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.db.session import get_db
from app.models.ticket import Ticket
from app.models.user import User
from app.web.templates import templates

router = APIRouter(tags=["agent"])

STATUSES = ["new", "in_progress", "waiting", "resolved", "closed"]



@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("agent")),
    ):
    my_count = await db.scalar(
        select(func.count()).select_from(Ticket).where(
            Ticket.assignee_id == user.id,
            Ticket.status.in_(["new", "in_progress", "waiting"]),
        )
    )
    unassigned_count = await db.scalar(
        select(func.count()).select_from(Tiket).where(
            Ticket.assignee_id.is_(None),
            Ticket.status == "new",
        )
    )
   overdue = 0
   resolved_today = 0

   result = await db.execute(
    select(Ticket).where(
        Ticket.assignee_id == user.id,
        Ticket.status.in_(["new", "in_progress", "waiting"]),
    ).order_by(Ticket.sreated_att.desc().limit(5))
   )
   unassigned_tickets = result.scalars().all()

    return templates.TemplateResponse(
        "agent/dashboard.html",
        {"request": request,
         "user": MOCK_AGENT,
          "stats": {
            "my_open": my_count or 0,
            "unassigned": unassigned_count or 0,
            "overdue": overdue,
            "resolved_today": resolved_today,
          },
         "my_tickets": my_tickets,
          "unassigned_tickets": unassigned_tickets},
    )


@router.get("/tickets", response_class=HTMLResponse)
async def tickets(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("agent", "manager")),
):
    result = await db.execute(
        select(Ticket)order_by(Ticket.created_at.desc())
    )
    tickets_list = result.scas=lars().all()
    return templates.TemplateResponse(
        "agent/tickets.html",
        {"request": request, "user": MOCK_AGENT,
         "tickets": tickets_list},
    )


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
        "client": "Ромашка",
        "client_contact": "Иван Петров",
        "client_email": "ivan@romashka.ru",
        "created": "12.10.2026 09:14",
        "updated": "12.10.2026 10:35",
        "sla_deadline": "12.10.2026 13:14",
        "sla_status": "Осталось 1 ч 20 мин",
        "sla_color": "warning",
        "assignee": "Алексей Смирнов",
        "description": (
            "При попытке входа в систему появляется ошибка "
            "«Неверный логин или пароль», хотя данные введены верно. "
            "Проблема воспроизводится у всех сотрудников отдела продаж."
        ),
    }

    comments = [
        {"author": "Иван Петров", "role": "Клиент",
         "created": "12.10.2026 09:14", "is_staff": False,
         "text": "При попытке входа появляется ошибка. Скриншот прилагаю."},
        {"author": "Алексей Смирнов", "role": "Агент L1",
         "created": "12.10.2026 09:32", "is_staff": True,
         "text": "Здравствуйте! Принял заявку в работу, проверяю логи авторизации."},
        {"author": "Алексей Смирнов", "role": "Агент L1",
         "created": "12.10.2026 10:35", "is_staff": True,
         "text": "Нашли причину: проблема на стороне сервиса аутентификации. "
                 "Передал задачу инженеру L2."},
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

    statuses = [
        {"value": "new", "label": "Новый"},
        {"value": "in_progress", "label": "В работе"},
        {"value": "waiting", "label": "Ожидает ответа"},
        {"value": "resolved", "label": "Решён"},
        {"value": "closed", "label": "Закрыт"},
    ]

    return templates.TemplateResponse(
        "agent/ticket_detail.html",
        {
            "request": request,
            "user": MOCK_AGENT,
            "ticket": ticket,
            "comments": comments,
            "history": history,
            "statuses": statuses,
        },
    )