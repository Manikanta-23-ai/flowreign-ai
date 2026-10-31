
from pydantic import BaseModel, Field


class CSVAnalysisRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    csv_content: str = Field(min_length=1, max_length=5_000_000)
