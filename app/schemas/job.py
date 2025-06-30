from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, List
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company_name: Optional[str] = None
    location: Optional[str]
    url: HttpUrl
    source: str
    job_id: str
    publication_date: datetime
    tags: Optional[List[str]] = []
    salary: Optional[str]
    job_type: Optional[str]

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, value):
        if isinstance(value, str):
            return [tag.strip() for tag in value.split(",") if tag.strip()]
        if value is None:
            return []
        return value or []

class JobCreate(JobBase):
    @field_validator("tags", mode="before")
    @classmethod
    def join_tags(cls, value):
        if isinstance(value, list):
            return ",".join(tag.strip() for tag in value if tag.strip()) if value else None
        return value

class JobSchema(JobBase):
    id: int
    scraped_at: datetime

    class Config:
        from_attributes = True
