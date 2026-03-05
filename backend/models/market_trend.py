from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class MarketTrend(Base):
    __tablename__ = "market_trends"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    platform: Mapped[str] = mapped_column(String(48), nullable=False)
    time_range: Mapped[str] = mapped_column(String(16), nullable=False)
    search_volume: Mapped[int] = mapped_column(Integer, nullable=False)
    social_mentions: Mapped[int] = mapped_column(Integer, nullable=False)
    growth_rate: Mapped[float] = mapped_column(Float, nullable=False)
    product_count: Mapped[int] = mapped_column(Integer, nullable=False)
    supply_demand_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
