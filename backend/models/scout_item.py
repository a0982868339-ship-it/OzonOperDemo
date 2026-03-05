from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class ScoutItem(Base):
    __tablename__ = "scout_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    raw_id: Mapped[int] = mapped_column(ForeignKey("scout_raw.id"), nullable=False)
    keyword: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(8), nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    reviews: Mapped[int] = mapped_column(Integer, nullable=True)
    sales_estimate: Mapped[int] = mapped_column(Integer, nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=True)
    subcategory: Mapped[str] = mapped_column(String(64), nullable=True)
    platform: Mapped[str] = mapped_column(String(32), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
