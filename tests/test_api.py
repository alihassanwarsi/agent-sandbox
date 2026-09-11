from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)

def test_run_low_risk_request_completes_immediately():
    response = client.post("/agent/run", json={"user_message": "What is 5 + 5?", "role": "VIEWER"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert "10" in body["final_response"]


def test_run_high_risk_request_pauses_for_approval():
    response = client.post(
        "/agent/run",
        json={"user_message": "Create a ticket titled 'Test' with description 'Testing'", "role": "OPERATOR"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "awaiting_approval"
    assert "approval_request_id" in body

def test_full_approval_flow_over_http():
    run_response = client.post(
        "/agent/run",
        json={"user_message": "Create a ticket titled 'Outage' with description 'Prod down'", "role": "OPERATOR"},
    )
    run_body = run_response.json()
    thread_id = run_body["thread_id"]
    request_id = run_body["approval_request_id"]

    pending_response = client.get("/approvals/pending")
    assert any(r["id"] == request_id for r in pending_response.json())

    approve_response = client.post(f"/approvals/{request_id}/approve", json={"decided_by": "test_user"})
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    resume_response = client.post(f"/agent/resume/{thread_id}", json={"outcome": "approved"})
    assert resume_response.status_code == 200
    resume_body = resume_response.json()
    assert resume_body["status"] == "completed"
    assert "TICKET-" in resume_body["final_response"]

def test_reject_flow_over_http():
    run_response = client.post(
        "/agent/run",
        json={"user_message": "Create a ticket titled 'Bad idea' with description 'Not needed'", "role": "OPERATOR"},
    )
    run_body = run_response.json()
    thread_id = run_body["thread_id"]
    request_id = run_body["approval_request_id"]

    reject_response = client.post(
        f"/approvals/{request_id}/reject", json={"decided_by": "test_user", "reason": "Not necessary."}
    )
    assert reject_response.status_code == 200

    resume_response = client.post(
        f"/agent/resume/{thread_id}", json={"outcome": "rejected", "reason": "Not necessary."}
    )
    resume_body = resume_response.json()
    assert resume_body["status"] == "completed"
    assert "rejected" in resume_body["final_response"].lower()

def test_unknown_role_returns_400():
    response = client.post("/agent/run", json={"user_message": "Hello", "role": "SUPERUSER"})
    assert response.status_code == 400

def test_approving_unknown_request_returns_404():
    response = client.post("/approvals/does-not-exist/approve", json={"decided_by": "test_user"})
    assert response.status_code == 404

def test_analytics_endpoint_returns_data():
    response = client.get("/analytics")
    assert response.status_code == 200
    body = response.json()
    assert "total_runs" in body