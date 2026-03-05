from datetime import date
from sqlalchemy import String, Integer, Float, Date
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class ShopPerformance(Base):
    __tablename__ = "shop_performance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shop_id: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(64), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    sales_units: Mapped[int] = mapped_column(Integer, nullable=False)
    revenue: Mapped[float] = mapped_column(Float, nullable=False)
    profit: Mapped[float] = mapped_column(Float, nullable=False)
    exposure: Mapped[int] = mapped_column(Integer, nullable=False)
    conversion_rate: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    competitor_avg_price: Mapped[float] = mapped_column(Float, nullable=False)
    price_index: Mapped[float] = mapped_column(Float, nullable=False)
    supply_demand_score: Mapped[float] = mapped_column(Float, nullable=False)
