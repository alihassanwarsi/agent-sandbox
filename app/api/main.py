import uuid
from fastapi import FastAPI, HTTPException
from app.agent.graph import run_agent, resume_agent
from app.api.schemas import ApproveRequest, ModifyRequest, RejectRequest, ResumeRequest, RunRequest
from app.db.postgres_queue import PostgresApprovalQueue
from app.observability.analytics import compute_safety_analytics
from app.observability.trace_viewer import format_trace
from app.permissions.roles import UserRole
from app.tools.setup import build_default_registry

app = FastAPI(title="Permissioned Tool-Using Agent Sandbox")

_registry = build_default_registry()
_queue = PostgresApprovalQueue()

from app.agent.graph import _trace_store

def _parse_role(role_str: str) -> UserRole:
    try:
        return UserRole[role_str.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Unknown role '{role_str}'.")

@app.post("/agent/run")
def api_run_agent(request: RunRequest):
    role = _parse_role(request.role)
    thread_id = request.thread_id or str(uuid.uuid4())

    result = run_agent(request.user_message, role, _registry, _queue, thread_id)

    if result["status"] == "completed":
        return {"status": "completed", "thread_id": thread_id, "final_response": result["state"].final_response}

    return {"status": "awaiting_approval", "thread_id": thread_id, "approval_request_id": result["approval_request_id"]}

@app.post("/agent/resume/{thread_id}")
def api_resume_agent(thread_id: str, request: ResumeRequest):
    decision = {"outcome": request.outcome, "tool_input": request.tool_input, "reason": request.reason}
    result = resume_agent(thread_id, decision, _registry, _queue)

    if result["status"] == "completed":
        return {"status": "completed", "final_response": result["state"].final_response}

    return {"status": "awaiting_approval", "approval_request_id": result["approval_request_id"]}

@app.get("/approvals/pending")
def api_list_pending():
    return _queue.list_pending()

@app.post("/approvals/{request_id}/approve")
def api_approve(request_id: str, request: ApproveRequest):
    try:
        return _queue.approve(request_id, decided_by=request.decided_by)
    except KeyError:
        raise HTTPException(status_code=404, detail="Approval request not found.")

@app.post("/approvals/{request_id}/reject")
def api_reject(request_id: str, request: RejectRequest):
    try:
        return _queue.reject(request_id, decided_by=request.decided_by, reason=request.reason)
    except KeyError:
        raise HTTPException(status_code=404, detail="Approval request not found.")

@app.post("/approvals/{request_id}/modify")
def api_modify(request_id: str, request: ModifyRequest):
    try:
        return _queue.modify(request_id, decided_by=request.decided_by, new_tool_input=request.tool_input, reason=request.reason)
    except KeyError:
        raise HTTPException(status_code=404, detail="Approval request not found.")

@app.get("/analytics")
def api_analytics():
    return compute_safety_analytics(_trace_store, _queue)

@app.get("/traces/{trace_id}")
def api_trace(trace_id: str):
    return {"trace": format_trace(_trace_store, trace_id)}

@app.post("/approvals/{request_id}/approve-and-resume")
def api_approve_and_resume(request_id: str, request: ApproveRequest):
    try:
        approved = _queue.approve(request_id, decided_by=request.decided_by)
    except KeyError:
        raise HTTPException(status_code=404, detail="Approval request not found.")

    result = resume_agent(approved.thread_id, {"outcome": "approved"}, _registry, _queue)
    if result["status"] == "completed":
        return {"status": "completed", "final_response": result["state"].final_response}
    return {"status": "awaiting_approval", "approval_request_id": result["approval_request_id"]}

@app.post("/approvals/{request_id}/reject-and-resume")
def api_reject_and_resume(request_id: str, request: RejectRequest):
    try:
        rejected = _queue.reject(request_id, decided_by=request.decided_by, reason=request.reason)
    except KeyError:
        raise HTTPException(status_code=404, detail="Approval request not found.")

    result = resume_agent(rejected.thread_id, {"outcome": "rejected", "reason": request.reason}, _registry, _queue)
    if result["status"] == "completed":
        return {"status": "completed", "final_response": result["state"].final_response}
    return {"status": "awaiting_approval", "approval_request_id": result["approval_request_id"]}

@app.post("/approvals/{request_id}/modify-and-resume")
def api_modify_and_resume(request_id: str, request: ModifyRequest):
    try:
        modified = _queue.modify(request_id, decided_by=request.decided_by, new_tool_input=request.tool_input, reason=request.reason)
    except KeyError:
        raise HTTPException(status_code=404, detail="Approval request not found.")

    result = resume_agent(modified.thread_id, {"outcome": "modified", "tool_input": request.tool_input}, _registry, _queue)
    if result["status"] == "completed":
        return {"status": "completed", "final_response": result["state"].final_response}
    return {"status": "awaiting_approval", "approval_request_id": result["approval_request_id"]}