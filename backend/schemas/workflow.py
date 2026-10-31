
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    RUNNING = "running"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowCreate(BaseModel):
    objective: str = Field(
        min_length=5,
        max_length=2000,
        description="The business objective to accomplish."
    )
    priority: WorkflowPriority = WorkflowPriority.MEDIUM
    requires_approval: bool = True


class WorkflowResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    objective: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    priority: WorkflowPriority = WorkflowPriority.MEDIUM
    requires_approval: bool = True
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    result: Optional[str] = None
