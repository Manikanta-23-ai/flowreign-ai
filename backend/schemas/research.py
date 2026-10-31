from pydantic import BaseModel, Field, HttpUrl


class ResearchRequest(BaseModel):
    objective: str = Field(min_length=5, max_length=1000)
    source_urls: list[HttpUrl] = Field(min_length=1, max_length=5)