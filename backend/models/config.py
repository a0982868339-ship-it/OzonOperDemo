from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class Config(Base):
    __tablename__ = "config"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False)  # Scout, Analyst, Linguist, Creative, Orchestrator
    provider_name: Mapped[str] = mapped_column(String(32), nullable=False) # OpenAI, DeepSeek, Anthropic
    base_url: Mapped[str] = mapped_column(String(255), nullable=True)
    model_id: Mapped[str] = mapped_column(String(128), nullable=False)
    api_key_encrypted: Mapped[str] = mapped_column(String(512), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

class PlatformWeight(Base):
    __tablename__ = "platform_weights"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    platform_name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False) # VK, OK, YouTube, Ozon, WB, Yandex
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
