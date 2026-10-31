
import pytest
from fastapi.testclient import TestClient

from backend.main import app
import backend.database.connection as database
import core.engine.executor as executor


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "test_flowreign.db",
    )

    with TestClient(app) as test_client:
        yield test_client


def create_and_plan(client, objective="Analyze business performance"):
    created = client.post(
        "/api/v1/workflows",
        json={
            "objective": objective,
            "priority": "high",
            "requires_approval": True,
        },
    )

    assert created.status_code == 201
    workflow_id = created.json()["id"]

    planned = client.post(
        f"/api/v1/workflows/{workflow_id}/plan"
    )

    assert planned.status_code == 200
    assert planned.json()["total_tasks"] == 5

    return workflow_id


def test_create_and_list_workflows(client):
    response = client.post(
        "/api/v1/workflows",
        json={
            "objective": "Analyze customer feedback",
            "priority": "medium",
            "requires_approval": True,
        },
    )

    assert response.status_code == 201

    workflow_id = response.json()["id"]
    listing = client.get("/api/v1/workflows")

    assert listing.status_code == 200
    assert any(
        item["id"] == workflow_id
        for item in listing.json()
    )


def test_workflow_plan_is_persisted(client):
    workflow_id = create_and_plan(client)

    response = client.get(
        f"/api/v1/workflows/{workflow_id}/tasks"
    )

    assert response.status_code == 200
    assert len(response.json()["tasks"]) == 5


def test_execution_requires_approval(client):
    workflow_id = create_and_plan(client)

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/execute"
    )

    assert response.status_code == 409
    assert "approval" in response.json()["detail"].lower()


def test_approved_workflow_executes_sequentially(
    client,
    monkeypatch,
):
    workflow_id = create_and_plan(client)

    approval = client.post(
        f"/api/v1/workflows/{workflow_id}/approve",
        json={
            "approved": True,
            "note": "Approved for AI processing",
        },
    )

    assert approval.status_code == 200

    execution_order = []

    def fake_specialist(task, objective, previous_results):
        execution_order.append(task["title"])

        return (
            f"{task['assigned_agent']} completed "
            f"the task: {task['title']}"
        )

    monkeypatch.setattr(
        executor,
        "execute_specialist",
        fake_specialist,
    )

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/execute"
    )

    assert response.status_code == 200, response.text

    result = response.json()

    assert result["execution_status"] == "completed"
    assert result["completed_tasks"] == 5
    assert len(execution_order) == 5

    workflow = client.get(
        f"/api/v1/workflows/{workflow_id}"
    )

    assert workflow.json()["status"] == "completed"

    tasks = client.get(
        f"/api/v1/workflows/{workflow_id}/tasks"
    ).json()["tasks"]

    assert all(task["status"] == "completed" for task in tasks)
    assert all(task["output"] for task in tasks)


def test_failed_agent_marks_workflow_failed(
    client,
    monkeypatch,
):
    workflow_id = create_and_plan(client)

    approval = client.post(
        f"/api/v1/workflows/{workflow_id}/approve",
        json={"approved": True},
    )

    assert approval.status_code == 200

    def failing_specialist(task, objective, previous_results):
        raise RuntimeError("Simulated agent failure")

    monkeypatch.setattr(
        executor,
        "execute_specialist",
        failing_specialist,
    )

    response = client.post(
        f"/api/v1/workflows/{workflow_id}/execute"
    )

    assert response.status_code == 502

    workflow = client.get(
        f"/api/v1/workflows/{workflow_id}"
    )

    assert workflow.json()["status"] == "failed"
