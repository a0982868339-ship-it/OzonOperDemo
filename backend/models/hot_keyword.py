"""
HotKeyword — 每日热词快照表

每天 06:00 由 DataCollectJob 写入，前端三个页面从此表读取。
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from backend.core.database import Base


class HotKeyword(Base):
    __tablename__ = "hot_keywords"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    keyword     = Column(String(120), nullable=False, index=True)
    keyword_ru  = Column(String(180), nullable=True)   # 俄语原词（如来自 VK/Ozon）
    category    = Column(String(64),  nullable=False, default="general")
    platform    = Column(String(48),  nullable=False)  # google|youtube|ozon|vk
    # 热度指标
    search_volume   = Column(Integer, nullable=False, default=0)   # 绝对搜索量
    trend_score     = Column(Float,   nullable=False, default=0.0) # 标准化 0-100
    growth_rate     = Column(Float,   nullable=False, default=0.0) # 环比增长率 (-1 ~ +N)
    # 日期维度
    snapshot_date   = Column(Date,    nullable=False, default=date.today, index=True)
    created_at      = Column(DateTime, nullable=False, default=datetime.utcnow)
