import csv
import io
import json

from fastapi import HTTPException

from backend.database.connection import get_db_connection


def get_workflow_report(workflow_id: str) -> dict:
    with get_db_connection() as connection:
        workflow = connection.execute(
            "SELECT * FROM workflows WHERE id = ?",
            (workflow_id,),
        ).fetchone()

        if workflow is None:
            raise HTTPException(status_code=404, detail="Workflow not found.")

        tasks = connection.execute(
            """
            SELECT task_id, title, assigned_agent, description,
                   depends_on, status, requires_human_approval,
                   created_at, output
            FROM workflow_tasks
            WHERE workflow_id = ?
            ORDER BY created_at, task_id
            """,
            (workflow_id,),
        ).fetchall()

        approval = connection.execute(
            """
            SELECT decision, note, decided_at
            FROM workflow_approvals
            WHERE workflow_id = ?
            """,
            (workflow_id,),
        ).fetchone()

    return {
        "platform": "FlowReign AI",
        "report_type": "Workflow Execution Report",
        "workflow": dict(workflow),
        "approval": dict(approval) if approval else None,
        "tasks": [
            {
                **dict(task),
                "depends_on": json.loads(task["depends_on"] or "[]"),
                "output": (
                    json.loads(task["output"])
                    if task["output"]
                    else None
                ),
            }
            for task in tasks
        ],
        "task_summary": {
            "total": len(tasks),
            "completed": sum(t["status"] == "completed" for t in tasks),
            "failed": sum(t["status"] == "failed" for t in tasks),
            "pending": sum(
                t["status"] in ("planned", "pending", "running")
                for t in tasks
            ),
        },
    }


def workflow_report_csv(workflow_id: str) -> str:
    report = get_workflow_report(workflow_id)

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "workflow_id",
            "objective",
            "workflow_status",
            "task_id",
            "task_title",
            "assigned_agent",
            "task_status",
            "requires_approval",
            "task_output",
        ],
    )

    writer.writeheader()

    workflow = report["workflow"]

    for task in report["tasks"]:
        writer.writerow({
            "workflow_id": workflow["id"],
            "objective": workflow["objective"],
            "workflow_status": workflow["status"],
            "task_id": task["task_id"],
            "task_title": task["title"],
            "assigned_agent": task["assigned_agent"],
            "task_status": task["status"],
            "requires_approval": task["requires_human_approval"],
            "task_output": json.dumps(task["output"], ensure_ascii=False),
        })

    return output.getvalue()