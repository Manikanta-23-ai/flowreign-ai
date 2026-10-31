from datetime import datetime, timezone

from backend.services.research_service import research_sources
from backend.services.data_service import analyze_csv, DataAnalysisError


def run_operations(objective, source_urls, csv_filename=None, csv_content=None):
    results = {
        "platform": "FlowReign AI",
        "objective": objective,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "components": {},
    }

    if source_urls:
        results["components"]["research"] = research_sources(
            objective,
            source_urls,
        )
    else:
        results["components"]["research"] = {
            "status": "skipped",
            "reason": "No source URLs supplied.",
        }

    if csv_content:
        try:
            results["components"]["data_analysis"] = analyze_csv(
                csv_filename or "uploaded.csv",
                csv_content,
            )
        except DataAnalysisError as error:
            results["components"]["data_analysis"] = {
                "status": "failed",
                "error": str(error),
            }
    else:
        results["components"]["data_analysis"] = {
            "status": "skipped",
            "reason": "No CSV supplied.",
        }

    results["completed_at"] = datetime.now(timezone.utc).isoformat()
    results["execution_mode"] = "deterministic orchestration"
    results["external_actions_executed"] = False

    return results