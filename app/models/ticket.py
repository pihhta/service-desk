from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.client import Client
from app.models.product import Product
from app.models.user import User

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="new")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    client: Mapped["Client"] = relationship(lazy="joined")  # noqa: F821
    product: Mapped["Product | None"] = relationship(lazy="joined")  # noqa: F821
    author: Mapped["User"] = relationship(foreign_keys=[author_id], lazy="joined")  # noqa: F821
    assignee: Mapped["User | None"] = relationship(foreign_keys=[assignee_id], lazy="joined")  # noqa: F821
