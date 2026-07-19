from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Product(Base):
    """Minimal read mapping; schema ownership remains in database/mysql/schema.sql."""

    __tablename__ = "product"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_code: Mapped[str] = mapped_column(String(40), unique=True)
    product_name: Mapped[str] = mapped_column(String(200))
    subtitle: Mapped[str | None] = mapped_column(String(255))
    raw_ingredient_text: Mapped[str] = mapped_column(Text)
    sale_status: Mapped[str] = mapped_column(String(24))
    review_status: Mapped[str] = mapped_column(String(24))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
