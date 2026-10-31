import json

from fastapi import APIRouter
from fastapi.responses import Response

from backend.services.report_service import (
    get_workflow_report,
    workflow_report_csv,
)

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports & Exports"],
)


@router.get("/{workflow_id}/json")
def download_json_report(workflow_id: str):
    report = get_workflow_report(workflow_id)

    return Response(
        content=json.dumps(report, indent=2, ensure_ascii=False),
        media_type="application/json",
        headers={
            "Content-Disposition":
                f'attachment; filename="flowreign-{workflow_id}.json"'
        },
    )


@router.get("/{workflow_id}/csv")
def download_csv_report(workflow_id: str):
    report_csv = workflow_report_csv(workflow_id)

    return Response(
        content=report_csv,
        media_type="text/csv",
        headers={
            "Content-Disposition":
                f'attachment; filename="flowreign-{workflow_id}.csv"'
        },
    )