from pydantic import BaseModel, Field, HttpUrl


class OperationsRequest(BaseModel):
    objective: str = Field(min_length=5, max_length=1000)
    source_urls: list[HttpUrl] = Field(default_factory=list, max_length=5)
    csv_filename: str | None = Field(default=None, max_length=255)
    csv_content: str | None = Field(default=None, max_length=5_000_000)