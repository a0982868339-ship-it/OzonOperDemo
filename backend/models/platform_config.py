"""
models/platform_config.py — 平台数据源 API Key 配置表

存储各采集平台的 API 密钥（AES 加密）、开关状态、连通性测试时间。
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class PlatformConfig(Base):
    __tablename__ = "platform_config"

    id:              Mapped[int]           = mapped_column(primary_key=True, autoincrement=True)
    platform:        Mapped[str]           = mapped_column(String(32), unique=True, nullable=False)  # vk / ok / youtube / ozon / wb / yandex
    display_name:    Mapped[str]           = mapped_column(String(64), nullable=False)   # VK / OK / YouTube …
    color:           Mapped[str]           = mapped_column(String(16), default="#6366f1") # hex dot color
    keys_json:       Mapped[Optional[str]] = mapped_column(Text, nullable=True)          # JSON: {"VK_ACCESS_TOKEN": "enc:..."} — each value AES-encrypted
    is_active:       Mapped[bool]          = mapped_column(Boolean, default=True)
    status:          Mapped[str]           = mapped_column(String(16), default="pending") # pending / configured / error / no_key_needed
    status_msg:      Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    last_tested_at:  Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at:      Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SchedulerConfig(Base):
    __tablename__ = "scheduler_config"

    id:           Mapped[int]           = mapped_column(primary_key=True, autoincrement=True)
    collect_hour: Mapped[int]           = mapped_column(default=6)
    collect_min:  Mapped[int]           = mapped_column(default=0)
    summary_hour: Mapped[int]           = mapped_column(default=7)
    summary_min:  Mapped[int]           = mapped_column(default=50)
    timezone:     Mapped[str]           = mapped_column(String(64), default="Asia/Shanghai")
    webhook_url:  Mapped[Optional[str]] = mapped_column(String(512), nullable=True)  # 钉钉 / 飞书 webhook
    updated_at:   Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
