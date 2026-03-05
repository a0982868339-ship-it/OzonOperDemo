from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class AIAsset(Base):
    __tablename__ = "ai_assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    title_seo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bullet_points_ru: Mapped[Optional[List[Any]]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[List[Any]]] = mapped_column(JSON, nullable=True)
    urls: Mapped[Optional[List[Any]]] = mapped_column(JSON, nullable=True)
    prompt_text: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
