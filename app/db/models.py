from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import declared_attr
from app.db.database import Base

class ApprovalRequestORM(Base):
    __tablename__ = "approval_requests"

    id= Column(Integer, primary_key=True)
    tool_name = Column(String, nullable=False)
    tool_input = Column(JSON, nullable=False)
    risk_level = Column(String, nullable=False)
    role = Column(Integer, nullable=False)
    reasoning = Column(String, nullable=False)

    status = Column(String, nullable=False)

    decided_by = Column(String, nullable=True)
    decision_reason = Column(String, nullable=True)
    final_tool_input = Column(JSON, nullable=True)