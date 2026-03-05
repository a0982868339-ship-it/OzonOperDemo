from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.sqlite import JSON
from backend.core.database import Base


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    mode = Column(String(20), default="pipeline")   # pipeline | manual
    user_input = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending/running/done/failed

    # Per-agent status: idle / running / done / failed / skipped
    scout_status      = Column(String(20), default="idle")
    analyst_status    = Column(String(20), default="idle")
    linguistic_status = Column(String(20), default="idle")
    creative_status   = Column(String(20), default="idle")

    # Per-agent results (JSON blobs)
    scout_result      = Column(JSON, nullable=True)
    analyst_result    = Column(JSON, nullable=True)
    linguistic_result = Column(JSON, nullable=True)
    creative_result   = Column(JSON, nullable=True)

    # User-supplied overrides (allows skipping individual agents)
    user_scout_data_override = Column(JSON, nullable=True)   # skip Scout
    user_uploaded_copy       = Column(Text, nullable=True)   # skip Linguistic
    user_uploaded_image      = Column(String(512), nullable=True)  # skip Creative

    # Pipeline config flags
    use_scout      = Column(String(5), default="true")
    use_analyst    = Column(String(5), default="true")
    use_linguistic = Column(String(5), default="true")
    use_creative   = Column(String(5), default="true")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
