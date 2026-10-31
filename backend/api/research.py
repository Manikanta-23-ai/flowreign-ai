from fastapi import APIRouter, HTTPException

from backend.schemas.research import ResearchRequest
from backend.services.research_service import research_sources

router = APIRouter(
    prefix="/api/v1/research",
    tags=["Evidence Research"],
)


@router.post("/collect")
def collect_research(data: ResearchRequest):
    try:
        return research_sources(
            objective=data.objective,
            source_urls=[str(url) for url in data.source_urls],
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error