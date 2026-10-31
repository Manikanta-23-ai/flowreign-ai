
import json
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from core.engine.planner import build_plan
from core.engine.executor import (
    persist_plan,
    get_workflow_tasks,
    record_approval,
    run_approved_workflow,
    WorkflowExecutionError,
)

from backend.schemas.workflow import (
    WorkflowCreate,
    WorkflowResponse,
    WorkflowStatus,
)
from backend.services.workflow_service import (
    create_workflow,
    get_workflow,
    list_workflows,
    update_workflow,
)


router = APIRouter(
    prefix="/api/v1/workflows",
    tags=["Workflows"],
)


class WorkflowUpdate(BaseModel):
    status: WorkflowStatus
    result: Optional[str] = Field(default=None, max_length=10000)


class ApprovalRequest(BaseModel):
    approved: bool
    note: Optional[str] = Field(default=None, max_length=2000)


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_workflow(data: WorkflowCreate):
    return create_workflow(data)


@router.get("", response_model=list[WorkflowResponse])
def get_all_workflows():
    return list_workflows()


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow_by_id(workflow_id: str):
    workflow = get_workflow(workflow_id)

    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found.")

    return workflow


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
def update_existing_workflow(
    workflow_id: str,
    data: WorkflowUpdate,
):
    workflow = update_workflow(
        workflow_id=workflow_id,
        status=data.status,
        result=data.result,
    )

    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found.")

    return workflow


@router.post("/{workflow_id}/plan")
def plan_workflow(workflow_id: str):
    workflow = get_workflow(workflow_id)

    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found.")

    if workflow.status in (
        WorkflowStatus.RUNNING,
        WorkflowStatus.COMPLETED,
        WorkflowStatus.CANCELLED,
    ):
        raise HTTPException(
            status_code=409,
            detail="Cannot regenerate a plan for this workflow state.",
        )

    plan = build_plan(
        objective=workflow.objective,
        requires_approval=workflow.requires_approval,
    )

    persist_plan(workflow_id, plan)

    new_status = (
        WorkflowStatus.WAITING_FOR_APPROVAL
        if workflow.requires_approval
        else WorkflowStatus.PENDING
    )

    update_workflow(
        workflow_id,
        new_status,
        json.dumps(plan, indent=2),
    )

    return {
        **plan,
        "tasks_persisted": True,
        "next_action": (
            "Human approval required."
            if workflow.requires_approval
            else "Plan ready for execution."
        ),
    }


@router.get("/{workflow_id}/tasks")
def list_workflow_tasks(workflow_id: str):
    workflow = get_workflow(workflow_id)

    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found.")

    return {
        "workflow_id": workflow_id,
        "tasks": get_workflow_tasks(workflow_id),
    }


@router.post("/{workflow_id}/approve")
def approve_workflow(
    workflow_id: str,
    data: ApprovalRequest,
):
    workflow = get_workflow(workflow_id)

    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found.")

    tasks = get_workflow_tasks(workflow_id)

    if not tasks:
        raise HTTPException(
            status_code=400,
            detail="Generate a plan before requesting approval.",
        )

    if not workflow.requires_approval:
        raise HTTPException(
            status_code=400,
            detail="This workflow does not require approval.",
        )

    if workflow.status != WorkflowStatus.WAITING_FOR_APPROVAL:
        raise HTTPException(
            status_code=409,
            detail="Workflow is not waiting for approval.",
        )

    decision = record_approval(
        workflow_id,
        data.approved,
        data.note,
    )

    new_status = (
        WorkflowStatus.PENDING
        if data.approved
        else WorkflowStatus.CANCELLED
    )

    update_workflow(
        workflow_id,
        new_status,
        workflow.result,
    )

    return {
        **decision,
        "workflow_status": new_status.value,
        "execution_notice": (
            "Plan approved and ready for AI execution."
            if data.approved
            else "Plan rejected. No actions were executed."
        ),
    }


@router.post("/{workflow_id}/execute")
def execute_workflow(workflow_id: str):
    workflow = get_workflow(workflow_id)

    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found.")

    try:
        return run_approved_workflow(workflow_id)

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    except WorkflowExecutionError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
