"""
models/prompt_template.py — 提示词模板模型
用于存储和版本管理不同 Agent 的 System Prompt 及参数，替代硬编码
"""
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id:             Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    # The agent identifier this prompt belongs to (ex: "market_analyst", "video_gen")
    owner_agent:    Mapped[str]      = mapped_column(String(64), nullable=False)
    # Display name 
    name:           Mapped[str]      = mapped_column(String(128), nullable=False)
    # Version tag like "v1.0"
    version:        Mapped[str]      = mapped_column(String(32), nullable=False)
    
    # Prompt content
    system_prompt:  Mapped[str]      = mapped_column(Text, nullable=False, default="")
    user_template:  Mapped[str]      = mapped_column(Text, nullable=False, default="")
    
    # JSON for LLM configuration like {"temperature": 0.7, "max_tokens": 4096}
    parameters:     Mapped[dict]     = mapped_column(JSON, nullable=False, default=lambda: {})
    
    # Is this the currently active version for this agent? (Only one per agent should be active)
    is_active:      Mapped[bool]     = mapped_column(Boolean, default=False)

    created_at:     Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at:     Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
