"""
models/system_notice.py — 系统公告
管理员设置的站内公告，支持时间范围和类型（info/warning/success）
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class SystemNotice(Base):
    __tablename__ = "system_notices"

    id:          Mapped[int]           = mapped_column(primary_key=True, autoincrement=True)
    title:       Mapped[str]           = mapped_column(String(128), nullable=False)
    content:     Mapped[str]           = mapped_column(Text, nullable=False)
    notice_type: Mapped[str]           = mapped_column(String(16), default="info")   # info / warning / success / error
    is_active:   Mapped[bool]          = mapped_column(Boolean, default=True)
    pinned:      Mapped[bool]          = mapped_column(Boolean, default=False)
    expires_at:  Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by:  Mapped[str]           = mapped_column(String(64), nullable=False, default="admin")
    created_at:  Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)
    updated_at:  Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
