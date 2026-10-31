from fastapi import APIRouter, HTTPException

from backend.schemas.operations import OperationsRequest
from backend.services.operations_service import run_operations

router = APIRouter(
    prefix="/api/v1/operations",
    tags=["Unified Operations"],
)


@router.post("/run")
def run_unified_operations(data: OperationsRequest):
    if bool(data.csv_filename) != bool(data.csv_content):
        raise HTTPException(
            status_code=422,
            detail="Provide both csv_filename and csv_content, or neither.",
        )

    return run_operations(
        objective=data.objective,
        source_urls=[str(url) for url in data.source_urls],
        csv_filename=data.csv_filename,
        csv_content=data.csv_content,
    )