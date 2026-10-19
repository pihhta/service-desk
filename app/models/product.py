from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    version: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="active")