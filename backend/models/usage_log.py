from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(32), nullable=False)
    model_id: Mapped[str] = mapped_column(String(128), nullable=False)
    tokens_input: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_output: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_estimate: Mapped[float] = mapped_column(Float, nullable=False)
    request_path: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
