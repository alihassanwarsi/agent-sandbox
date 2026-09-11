from typing import Any, Optional
from pydantic import BaseModel

class RunRequest(BaseModel):
    user_message: str
    role: str
    thread_id: Optional[str] = None

class ResumeRequest(BaseModel):
    outcome: str
    tool_input: Optional[dict[str, Any]] = None
    reason: Optional[str] = None

class ApproveRequest(BaseModel):
    decided_by: str

class RejectRequest(BaseModel):
    decided_by: str
    reason: str

class ModifyRequest(BaseModel):
    decided_by: str
    tool_input: dict[str, Any]
    reason: str