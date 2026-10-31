
from typing import Optional

from backend.database.connection import get_db_connection
from backend.schemas.workflow import (
    WorkflowCreate,
    WorkflowResponse,
    WorkflowStatus,
)


def create_workflow(data: WorkflowCreate) -> WorkflowResponse:
    """Create and persist a new workflow."""

    workflow = WorkflowResponse(
        objective=data.objective,
        priority=data.priority,
        requires_approval=data.requires_approval,
    )

    record = workflow.model_dump(mode="json")

    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO workflows (
                id, objective, status, priority,
                requires_approval, created_at, result
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["id"],
                record["objective"],
                record["status"],
                record["priority"],
                int(record["requires_approval"]),
                record["created_at"],
                record["result"],
            ),
        )

    return workflow


def get_workflow(workflow_id: str) -> Optional[WorkflowResponse]:
    """Retrieve one workflow by its ID."""

    with get_db_connection() as connection:
        row = connection.execute(
            "SELECT * FROM workflows WHERE id = ?",
            (workflow_id,),
        ).fetchone()

    if row is None:
        return None

    record = dict(row)
    record["requires_approval"] = bool(record["requires_approval"])

    return WorkflowResponse.model_validate(record)


def list_workflows() -> list[WorkflowResponse]:
    """Retrieve all workflows, newest first."""

    with get_db_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM workflows ORDER BY created_at DESC"
        ).fetchall()

    workflows = []

    for row in rows:
        record = dict(row)
        record["requires_approval"] = bool(
            record["requires_approval"]
        )
        workflows.append(WorkflowResponse.model_validate(record))

    return workflows


def update_workflow(
    workflow_id: str,
    status: WorkflowStatus,
    result: Optional[str] = None,
) -> Optional[WorkflowResponse]:
    """Update a workflow's status and optional result."""

    with get_db_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM workflows WHERE id = ?",
            (workflow_id,),
        ).fetchone()

        if existing is None:
            return None

        connection.execute(
            """
            UPDATE workflows
            SET status = ?, result = ?
            WHERE id = ?
            """,
            (status.value, result, workflow_id),
        )

    return get_workflow(workflow_id)
