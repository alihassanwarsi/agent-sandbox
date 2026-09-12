from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base

class ApprovalRequestORM(Base):
    __tablename__ = "approval_requests"

    id = Column(String, primary_key=True)
    tool_name = Column(String, nullable=False)
    tool_input = Column(JSONB, nullable=False)
    risk_level = Column(Integer, nullable=False)
    role = Column(Integer, nullable=False)
    thread_id = Column(String, nullable=False)
    reasoning = Column(String, nullable=False)
    status = Column(String, nullable=False)
    decided_by = Column(String, nullable=True)
    decision_reason = Column(String, nullable=True)
    final_tool_input = Column(JSONB, nullable=True)