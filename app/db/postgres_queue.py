import uuid
from typing import Optional
from app.approval.models import ApprovalRequest, ApprovalStatus
from app.db.database import get_db_session
from app.db.models import ApprovalRequestORM
from app.permissions.risk import RiskLevel
from app.permissions.roles import UserRole

def _to_domain(row: ApprovalRequestORM) -> ApprovalRequest:
    """Convert a database row into our Pydantic domain model."""
    return ApprovalRequest(
        id=row.id,
        tool_name=row.tool_name,
        tool_input=row.tool_input,
        risk_level=RiskLevel(row.risk_level),
        role=UserRole(row.role),
        reasoning=row.reasoning,
        status=ApprovalStatus(row.status),
        decided_by=row.decided_by,
        decision_reason=row.decision_reason,
        final_tool_input=row.final_tool_input
    )

class PostgresApprovalQueue:
    """Same interface as ApprovalQueue, backed by a real Postgres table."""

    def submit(self, tool_name: str, tool_input: dict, risk_level: RiskLevel, role: UserRole,reasoning: str) -> ApprovalRequest:
        session = get_db_session()
        try:
            row = ApprovalRequestORM(
                id=str(uuid.uuid4()),
                tool_name=tool_name,
                tool_input=tool_input,
                risk_level=int(risk_level),
                role=int(role),
                reasoning=reasoning,
                status=ApprovalStatus.PENDING.value,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return _to_domain(row)
        finally:
            session.close()

    def get(self, request_id: str) -> ApprovalRequest:
        session = get_db_session()
        try:
            row = session.get(ApprovalRequestORM, request_id)
            if row is None:
                raise KeyError(f"No approval request found with id '{request_id}'.")
            return _to_domain(row)
        finally:
            session.close()

    def list_pending(self) -> list[ApprovalRequest]:
        session = get_db_session()
        try:
            rows = session.query(ApprovalRequestORM).filter_by(status=ApprovalStatus.PENDING.value).all()
            return [_to_domain(row) for row in rows]
        finally:
            session.close()

    def list_all(self) -> list[ApprovalRequest]:
        session = get_db_session()
        try:
            rows = session.query(ApprovalRequestORM).all()
            return [_to_domain(row) for row in rows]
        finally:
            session.close()

    def approve(self, request_id: str, decided_by: str) -> ApprovalRequest:
        session = get_db_session()
        try:
            row = session.get(ApprovalRequestORM, request_id)
            if row is None:
                raise KeyError(f"No approval request found with id '{request_id}'.")
            row.status = ApprovalStatus.APPROVED.value
            row.decided_by = decided_by
            row.final_tool_input = row.tool_input
            session.commit()
            session.refresh(row)
            return _to_domain(row)
        finally:
            session.close()

    def reject(self, request_id: str, decided_by: str, reason: str) -> ApprovalRequest:
        session = get_db_session()
        try:
            row = session.get(ApprovalRequestORM, request_id)
            if row is None:
                raise KeyError(f"No approval request found with id '{request_id}'.")
            row.status = ApprovalStatus.REJECTED.value
            row.decided_by = decided_by
            row.decision_reason = reason
            session.commit()
            session.refresh(row)
            return _to_domain(row)
        finally:
            session.close()

    def modify(self, request_id: str, decided_by: str, new_tool_input: dict, reason: str) -> ApprovalRequest:
        session = get_db_session()
        try:
            row = session.get(ApprovalRequestORM, request_id)
            if row is None:
                raise KeyError(f"No approval request found with id '{request_id}'.")
            row.status = ApprovalStatus.MODIFIED.value
            row.decided_by = decided_by
            row.decision_reason = reason
            row.final_tool_input = new_tool_input
            session.commit()
            session.refresh(row)
            return _to_domain(row)
        finally:
            session.close()

    def find_pending_for(self, tool_name: str, tool_input: dict, role: UserRole) -> Optional[ApprovalRequest]:
        session = get_db_session()
        try:
            row = (
                session.query(ApprovalRequestORM)
                .filter_by(status=ApprovalStatus.PENDING.value, tool_name=tool_name, role=int(role))
                .filter(ApprovalRequestORM.tool_input == tool_input)
                .first()
            )
            return _to_domain(row) if row else None
        finally:
            session.close()
