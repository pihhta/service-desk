from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.web.templates import templates

router = APIRouter(tags=["agent"])

MOCK_AGENT = {
    "role": "agent",
    "email": "a.smirnov@sd.ru",
    "full_name": "Александр Смирнов",
}

@router.get("/agent", response_class=HTMLResponse)
def dashboard(request: Request):

    stats = {
        "my_open": 5,
        "unassigned": 8,
        "overdue": 2,
        "resolved_today": 4,
    }
    my_tickets = [
        {"id": 101, "subject": "Ошибка авторизации", "client": "Ромашка",
         "status": "В работе", "status_color": "warning",
         "priority": "Высокий", "priority_color": "danger",
         "sla": "через 1 ч 20 мин", "sla_color": "warning",
         "updated": "10 мин назад"},
        {"id": 98, "subject": "Медленно работает раздел отчётов",
         "client": "ТехноСофт", "status": "В работе",
         "status_color": "warning", "priority": "Средний",
         "priority_color": "info", "sla": "через 4 ч",
         "sla_color": "secondary", "updated": "35 мин назад"},
        {"id": 95, "subject": "Не приходят уведомления на почту",
         "client": "Бета", "status": "Ожидает ответа",
         "status_color": "secondary", "priority": "Низкий",
         "priority_color": "secondary", "sla": "через 1 день",
         "sla_color": "success", "updated": "2 ч назад"},
    ]
    unassigned_tickets = [
        {"id": 105, "subject": "Ошибка при выгрузке отчёта",
         "client": "Ромashka", "priority": "Высокий",
         "priority_color": "danger", "created": "5 мин назад"},
        {"id": 104, "subject": "Не открывается раздел настроек",
         "client": "Альфа", "priority": "Средний",
         "priority_color": "info", "created": "20 мин назад"},
        {"id": 103, "subject": "Долго грузится главная",
         "client": "ТехноСофт", "priority": "Низкий",
         "priority_color": "secondary", "created": "1 ч назад"},
        {"id": 102, "subject": "Ошибка при сохранении клиента",
         "client": "Бета", "priority": "Высокий",
         "priority_color": "danger", "created": "1 ч 20 мин назад"},
    ]
    return templates.TemplateResponse( 
        "agent/dashboard.html",
        {"request": request, "user": MOCK_AGENT, "stats": stats,
         "my_tickets": my_tickets, "unassigned_tickets": unassigned_tickets},
        )
@router.get("/tickets", response_class=HTMLResponse)
def tickets(request: Request):
            return templates.TemplateResponse(
        "/agent/tickets.html",
        {"request": request, 'user': MOCK_AGENT, 'tickets': items},  # noqa: F821
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
        "/agent/ticket_detail.html",
        {
            "request": request,
            "user": MOCK_AGENT,
            "ticket": ticket,
            "comments": comments,
            "history": history,
            "statuses": statuses,
        },
    )