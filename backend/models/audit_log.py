"""
models/audit_log.py — 管理员操作审计日志
记录所有超管行为：谁 + 什么时间 + 做了什么 + 详情
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id:         Mapped[int]           = mapped_column(primary_key=True, autoincrement=True)
    operator:   Mapped[str]           = mapped_column(String(64), nullable=False)   # email of admin who did it
    action:     Mapped[str]           = mapped_column(String(64), nullable=False)   # e.g. "user.create", "platform.update"
    target:     Mapped[Optional[str]] = mapped_column(String(128), nullable=True)   # e.g. "user:123", "platform:vk"
    detail:     Mapped[Optional[str]] = mapped_column(Text, nullable=True)          # JSON or descriptive string
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime]      = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
