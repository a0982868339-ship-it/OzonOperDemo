from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class User(Base):
    __tablename__ = "users"

    id:              Mapped[int]           = mapped_column(primary_key=True, autoincrement=True)
    username:        Mapped[str]           = mapped_column(String(64), unique=True, nullable=False)
    email:           Mapped[str]           = mapped_column(String(120), unique=True, nullable=False)
    password_hash:   Mapped[str]           = mapped_column(String(256), nullable=False, default="")
    role:            Mapped[str]           = mapped_column(String(32), nullable=False, default="member")
    is_active:       Mapped[bool]          = mapped_column(Boolean, default=True)
    # VIP membership
    is_vip:          Mapped[bool]          = mapped_column(Boolean, default=False)
    vip_expires_at:  Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # AI token quota  (-1 = unlimited)
    token_quota:     Mapped[int]           = mapped_column(Integer, default=100_000)
    tokens_used:     Mapped[int]           = mapped_column(Integer, default=0)
    # Activity
    last_login_at:   Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at:      Mapped[datetime]      = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at:      Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
