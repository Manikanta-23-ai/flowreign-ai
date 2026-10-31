
import json
from datetime import datetime, timezone

from backend.database.connection import get_db_connection
from backend.schemas.workflow import WorkflowStatus
from backend.services.workflow_service import (
    get_workflow,
    update_workflow,
)
from core.agents.specialists import execute_specialist


class WorkflowExecutionError(Exception):
    pass


def persist_plan(workflow_id: str, plan: dict):
    now = datetime.now(timezone.utc).isoformat()

    with get_db_connection() as connection:
        connection.execute(
            "DELETE FROM workflow_tasks WHERE workflow_id = ?",
            (workflow_id,),
        )

        for task in plan["tasks"]:
            connection.execute(
                """
                INSERT INTO workflow_tasks (
                    task_id, workflow_id, title,
                    assigned_agent, description, depends_on,
                    status, requires_human_approval, created_at, output
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                """,
                (
                    f"{workflow_id}:{task['task_id']}",
                    workflow_id,
                    task["title"],
                    task["assigned_agent"],
                    task["description"],
                    json.dumps(task["depends_on"]),
                    task["status"],
                    int(task["requires_human_approval"]),
                    now,
                ),
            )

    return get_workflow_tasks(workflow_id)


def get_workflow_tasks(workflow_id: str):
    with get_db_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM workflow_tasks
            WHERE workflow_id = ?
            ORDER BY created_at, task_id
            """,
            (workflow_id,),
        ).fetchall()

    tasks = []

    for row in rows:
        task = dict(row)
        task["depends_on"] = json.loads(task["depends_on"])
        task["requires_human_approval"] = bool(
            task["requires_human_approval"]
        )
        tasks.append(task)

    return tasks


def record_approval(workflow_id: str, approved: bool, note=None):
    decision = "approved" if approved else "rejected"
    now = datetime.now(timezone.utc).isoformat()

    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO workflow_approvals (
                workflow_id, decision, note, decided_at
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(workflow_id) DO UPDATE SET
                decision = excluded.decision,
                note = excluded.note,
                decided_at = excluded.decided_at
            """,
            (workflow_id, decision, note, now),
        )

        connection.execute(
            """
            UPDATE workflow_tasks
            SET status = ?
            WHERE workflow_id = ?
            """,
            ("approved" if approved else "cancelled", workflow_id),
        )

    return {
        "workflow_id": workflow_id,
        "decision": decision,
        "decided_at": now,
        "note": note,
    }


def run_approved_workflow(workflow_id: str):
    workflow = get_workflow(workflow_id)

    if workflow is None:
        raise ValueError("Workflow not found.")

    if workflow.status != WorkflowStatus.PENDING:
        raise ValueError(
            f"Workflow must be pending before execution. "
            f"Current status: {workflow.status.value}"
        )

    if workflow.requires_approval:
        with get_db_connection() as connection:
            approval = connection.execute(
                """
                SELECT decision FROM workflow_approvals
                WHERE workflow_id = ?
                """,
                (workflow_id,),
            ).fetchone()

        if approval is None or approval["decision"] != "approved":
            raise ValueError(
                "Human approval is required before execution."
            )

    tasks = get_workflow_tasks(workflow_id)

    if not tasks:
        raise ValueError("Generate a workflow plan before execution.")

    completed_task_ids = set()
    previous_results = []

    update_workflow(
        workflow_id,
        WorkflowStatus.RUNNING,
        "AI workflow execution started.",
    )

    try:
        for task in tasks:
            dependencies = task["depends_on"]

            missing_dependencies = [
                dependency
                for dependency in dependencies
                if f"{workflow_id}:{dependency}" not in completed_task_ids
            ]

            if missing_dependencies:
                raise WorkflowExecutionError(
                    f"Dependencies are incomplete for task: "
                    f"{task['title']}. Missing: {missing_dependencies}"
                )

            with get_db_connection() as connection:
                connection.execute(
                    """
                    UPDATE workflow_tasks
                    SET status = 'running'
                    WHERE task_id = ?
                    """,
                    (task["task_id"],),
                )

            output = execute_specialist(
                task=task,
                objective=workflow.objective,
                previous_results=previous_results,
            )

            if not isinstance(output, str) or not output.strip():
                raise WorkflowExecutionError(
                    f"Agent returned empty output for: {task['title']}"
                )

            with get_db_connection() as connection:
                connection.execute(
                    """
                    UPDATE workflow_tasks
                    SET status = 'completed', output = ?
                    WHERE task_id = ?
                    """,
                    (output, task["task_id"]),
                )

            completed_task_ids.add(task["task_id"])

            previous_results.append({
                "task_id": task["task_id"],
                "title": task["title"],
                "agent": task["assigned_agent"],
                "output": output,
            })

    except Exception as error:
        with get_db_connection() as connection:
            connection.execute(
                """
                UPDATE workflow_tasks
                SET status = 'failed'
                WHERE workflow_id = ? AND status = 'running'
                """,
                (workflow_id,),
            )

        failure_message = (
            f"Workflow execution failed: {type(error).__name__}: {error}"
        )

        update_workflow(
            workflow_id,
            WorkflowStatus.FAILED,
            failure_message,
        )

        raise WorkflowExecutionError(failure_message) from error

    final_report = {
        "workflow_id": workflow_id,
        "objective": workflow.objective,
        "execution_status": "completed",
        "completed_tasks": len(previous_results),
        "task_results": previous_results,
        "limitations": [
            "Outputs were generated by an AI model.",
            "No external business actions were performed.",
            "Research was not independently verified against live sources.",
        ],
    }

    report_json = json.dumps(final_report, indent=2)

    update_workflow(
        workflow_id,
        WorkflowStatus.COMPLETED,
        report_json,
    )

    return final_report
