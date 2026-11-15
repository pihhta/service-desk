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

MOCK_CLIENT = {
    "role": "client",
    "email": "ivan@romashka.ru",
    "full_name": "Иван Петров",
    "company": "Ромашка",
}


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    stats = {
        "open": 3,
        "in_progress": 2,
        "resolved": 12,
        "total": 17,
    }
    recent_tickets = [
        {"id": 101, "subject": "Ошибка авторизации", "status": "Новый",
         "status_color": "primary", "priority": "Высокий",
         "priority_color": "danger", "created": "12.10.2026 09:14"},
        {"id": 98, "subject": "Медленно работает раздел отчётов",
         "status": "В работе", "status_color": "warning",
         "priority": "Средний", "priority_color": "info",
         "created": "11.10.2026 15:21"},
        {"id": 95, "subject": "Не приходят уведомления на почту",
         "status": "В работе", "status_color": "warning",
         "priority": "Низкий", "priority_color": "secondary",
         "created": "10.10.2026 11:05"},
        {"id": 90, "subject": "Забыл пароль", "status": "Решён",
         "status_color": "success", "priority": "Высокий",
         "priority_color": "danger", "created": "08.10.2026 17:40"},
    ]
    return templates.TemplateResponse(
        "client/dashboard.html",
        {"request": request, "user": MOCK_CLIENT, "stats": stats,
         "recent_tickets": recent_tickets},
    )


@router.get("/tickets", response_class=HTMLResponse)
def tickets(request: Request):
    items = [
        {"id": 101, "subject": "Ошибка авторизации", "status": "Новый",
         "status_color": "primary", "priority": "Высокий",
         "priority_color": "danger", "category": "Доступ",
         "created": "12.10.2026 09:14", "updated": "12.10.2026 09:20"},
        {"id": 98, "subject": "Медленно работает раздел отчётов",
         "status": "В работе", "status_color": "warning",
         "priority": "Средний", "priority_color": "info",
         "category": "Производительность",
         "created": "11.10.2026 15:21", "updated": "12.10.2026 08:02"},
        {"id": 95, "subject": "Не приходят уведомления на почту",
         "status": "В работе", "status_color": "warning",
         "priority": "Низкий", "priority_color": "secondary",
         "category": "Интеграции",
         "created": "10.10.2026 11:05", "updated": "11.10.2026 14:30"},
        {"id": 90, "subject": "Забыл пароль", "status": "Решён",
         "status_color": "success", "priority": "Высокий",
         "priority_color": "danger", "category": "Доступ",
         "created": "08.10.2026 17:40", "updated": "08.10.2026 18:05"},
        {"id": 85, "subject": "Ошибка при экспорте в Excel",
         "status": "Закрыт", "status_color": "dark",
         "priority": "Средний", "priority_color": "info",
         "category": "Функциональность",
         "created": "05.10.2026 10:12", "updated": "06.10.2026 12:00"},
    ]
    return templates.TemplateResponse(
        "client/tickets.html",
        {"request": request, "user": MOCK_CLIENT, "tickets": items},
    )


@router.get("/tickets/new", response_class=HTMLResponse)
def ticket_create(request: Request):
    products = [
        {"id": 1, "name": "CRM Lite"},
        {"id": 2, "name": "CRM Pro"},
        {"id": 3, "name": "Billing"},
    ]
    categories = ["Доступ", "Ошибка", "Производительность",
                  "Интеграции", "Функциональность", "Другое"]
    priorities = [
        {"value": "low", "label": "Низкий"},
        {"value": "medium", "label": "Средний"},
        {"value": "high", "label": "Высокий"},
        {"value": "critical", "label": "Критический"},
    ]
    return templates.TemplateResponse(
        "client/ticket_create.html",
        {"request": request, "user": MOCK_CLIENT,
         "products": products, "categories": categories,
         "priorities": priorities},
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