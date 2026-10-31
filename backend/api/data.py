
from fastapi import APIRouter, HTTPException

from backend.schemas.data import CSVAnalysisRequest
from backend.services.data_service import (
    analyze_csv,
    DataAnalysisError,
)


router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data Intelligence"],
)


@router.post("/analyze")
def analyze_uploaded_csv(data: CSVAnalysisRequest):
    try:
        return analyze_csv(
            filename=data.filename,
            csv_content=data.csv_content,
        )
    except DataAnalysisError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

from fastapi import APIRouter, HTTPException

from backend.schemas.data import CSVAnalysisRequest
from backend.services.data_service import (
    analyze_csv,
    DataAnalysisError,
)


router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data Intelligence"],
)


@router.post("/analyze")
def analyze_uploaded_csv(data: CSVAnalysisRequest):
    try:
        return analyze_csv(
            filename=data.filename,
            csv_content=data.csv_content,
        )
    except DataAnalysisError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

from fastapi import APIRouter, HTTPException

from backend.schemas.data import CSVAnalysisRequest
from backend.services.data_service import (
    analyze_csv,
    DataAnalysisError,
)


router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data Intelligence"],
)


@router.post("/analyze")
def analyze_uploaded_csv(data: CSVAnalysisRequest):
    try:
        return analyze_csv(
            filename=data.filename,
            csv_content=data.csv_content,
        )
    except DataAnalysisError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error
