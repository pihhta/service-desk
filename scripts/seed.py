import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.product import Product
from app.models.ticket import Ticket
from app.models.user import User

try:
    from passlib.context import CryptContext
    _pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(p: str) -> str:
        return _pwd.hash(p)
except ImportError:
    def hash_password(p: str) -> str:
        # Fallback для случая, если passlib ещё не установлен
        return p


DATABASE_URL = os.getenv(
    "DATABASE_URL_SYNC",
    "postgresql+psycopg://postgres:postgres@db:5432/service_desk",
)


def seed() -> None:
    engine = create_engine(DATABASE_URL)

    with Session(engine) as session:
        # Защита от повторного запуска
        if session.scalar(select(User).limit(1)):
            print("БД уже содержит пользователей. Пропускаем seed.")
            return

        # ---------- Клиенты ----------
        clients = [
            Client(name="Ромашка", contact_person="Иван Петров",
                   email="ivan@romashka.ru", phone="+7 900 123-45-67"),
            Client(name="ТехноСофт", contact_person="Мария Сидорова",
                   email="m.sidorova@technosoft.ru", phone="+7 900 222-33-44"),
            Client(name="Альфа", contact_person="Олег Кузнецов",
                   email="o.kuznetsov@alfa.ru", phone="+7 900 555-66-77"),
            Client(name="Бета", contact_person="Анна Морозова",
                   email="anna@beta.io", phone="+7 900 888-99-00"),
        ]
        session.add_all(clients)
        session.flush()

        # ---------- Продукты ----------
        products = [
            Product(name="CRM Lite", version="2.4.1", status="active"),
            Product(name="CRM Pro", version="3.0.0", status="active"),
            Product(name="Billing", version="1.8.2", status="active"),
            Product(name="Analytics", version="0.9.5", status="beta"),
        ]
        session.add_all(products)
        session.flush()

        # ---------- Пользователи ----------
        users = [
            User(email="admin@example.com", password_hash=hash_password("admin"),
                 full_name="Администратор", role="admin"),
            User(email="a.smirnov@sd.ru", password_hash=hash_password("agent"),
                 full_name="Алексей Смирнов", role="agent"),
            User(email="o.ivanova@sd.ru", password_hash=hash_password("agent"),
                 full_name="Ольга Иванова", role="agent"),
            User(email="d.volkov@sd.ru", password_hash=hash_password("manager"),
                 full_name="Дмитрий Волков", role="manager"),
            User(email="ivan@romashka.ru", password_hash=hash_password("client"),
                 full_name="Иван Петров", role="client"),
            User(email="anna@beta.io", password_hash=hash_password("client"),
                 full_name="Анна Морозова", role="client"),
        ]
        session.add_all(users)
        session.flush()

        # Удобные ссылки
        agent_alexey = next(u for u in users if u.email == "a.smirnov@sd.ru")
        agent_olga = next(u for u in users if u.email == "o.ivanova@sd.ru")
        client_ivan = next(u for u in users if u.email == "ivan@romashka.ru")
        client_anna = next(u for u in users if u.email == "anna@beta.io")

        c_romashka, c_techno, c_alfa, c_beta = clients
        p_crm_lite, p_crm_pro, p_billing, _ = products

        now = datetime.utcnow()

        # ---------- Тикеты ----------
        tickets = [
            Ticket(
                subject="Ошибка авторизации",
                description="При попытке входа появляется ошибка "
                            "«Неверный логин или пароль», хотя данные верные.",
                status="in_progress", priority="high",
                client_id=c_romashka.id, product_id=p_crm_pro.id,
                author_id=client_ivan.id, assignee_id=agent_alexey.id,
                created_at=now - timedelta(hours=2),
                updated_at=now - timedelta(minutes=10),
            ),
            Ticket(
                subject="Медленно работает раздел отчётов",
                description="Раздел отчётов грузится более 30 секунд "
                            "при фильтрации по датам.",
                status="in_progress", priority="medium",
                client_id=c_techno.id, product_id=p_crm_pro.id,
                author_id=client_ivan.id, assignee_id=agent_alexey.id,
                created_at=now - timedelta(hours=5),
                updated_at=now - timedelta(minutes=35),
            ),
            Ticket(
                subject="Не приходят уведомления на почту",
                description="Уведомления о новых заявках не приходят "
                            "с прошлой недели.",
                status="waiting", priority="low",
                client_id=c_beta.id, product_id=p_billing.id,
                author_id=client_anna.id, assignee_id=agent_alexey.id,
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(hours=2),
            ),
            Ticket(
                subject="Ошибка при выгрузке отчёта",
                description="При экспорте отчёта в Excel появляется ошибка 500.",
                status="new", priority="high",
                client_id=c_romashka.id, product_id=p_crm_pro.id,
                author_id=client_ivan.id, assignee_id=None,
                created_at=now - timedelta(minutes=5),
                updated_at=now - timedelta(minutes=5),
            ),
            Ticket(
                subject="Не открывается раздел настроек",
                description="При переходе в раздел настроек страница не загружается.",
                status="new", priority="medium",
                client_id=c_alfa.id, product_id=p_crm_lite.id,
                author_id=client_ivan.id, assignee_id=None,
                created_at=now - timedelta(minutes=20),
                updated_at=now - timedelta(minutes=20),
            ),
            Ticket(
                subject="Ошибка при сохранении клиента",
                description="После заполнения карточки клиента появляется "
                            "ошибка валидации.",
                status="in_progress", priority="high",
                client_id=c_beta.id, product_id=p_crm_pro.id,
                author_id=client_anna.id, assignee_id=agent_olga.id,
                created_at=now - timedelta(hours=1, minutes=20),
                updated_at=now - timedelta(minutes=15),
            ),
            Ticket(
                subject="Забыл пароль",
                description="Не могу восстановить пароль — письмо не приходит.",
                status="resolved", priority="high",
                client_id=c_alfa.id, product_id=p_crm_lite.id,
                author_id=client_ivan.id, assignee_id=agent_alexey.id,
                created_at=now - timedelta(days=5),
                updated_at=now - timedelta(days=4),
            ),
        ]
        session.add_all(tickets)
        session.commit()

        print(f"Готово: {len(clients)} клиентов, {len(products)} продуктов, "
              f"{len(users)} пользователей, {len(tickets)} тикетов")


if __name__ == "__main__":
    seed()