from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.crud import search_jobs
from app.schemas.job import JobSchema
from typing import List, Optional

from app.tasks.scrape_tasks import scrape_and_store_jobs

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/jobs", response_model=List[JobSchema])
def read_jobs(
    query: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    limit: int = 20,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    return search_jobs(
        db,
        query=query,
        location=location,
        job_type=job_type,
        tags=tags,
        skip=skip,
        limit=limit
    )

@router.post("/scrape")
def trigger_scrape(query: str = "job"):
    scrape_and_store_jobs.delay(query)
    return {"message": f"Scraping task started for query '{query}'"}

@router.get("/health")
def health():
    return {"status": "ok"}
