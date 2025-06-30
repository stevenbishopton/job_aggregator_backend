from sqlalchemy.orm import Session
from app.db import models
from app.schemas.job import JobCreate
from app.db.models import Job

def create_job(db: Session, job: JobCreate):
    existing_job = db.query(models.Job).filter(models.Job.job_id == job.job_id).first()
    if existing_job:
        return existing_job

    db_job = models.Job(
        title=job.title,
        company_name=job.company_name,
        location=job.location,
        url=str(job.url),
        source=job.source,
        job_id=job.job_id,
        publication_date=job.publication_date,
        tags=",".join(job.tags) if job.tags else None,
        salary=job.salary,
        job_type=job.job_type,
    )
    db.add(db_job)
    return db_job

def get_all_jobs(db: Session, skip: int = 0, limit: int = 20):
    return db.query(models.Job).offset(skip).limit(limit).all()

def save_jobs(db: Session, jobs: list[JobCreate]):
    added = 0
    for job in jobs:
        if db.query(models.Job).filter_by(job_id=job.job_id).first():
            continue
        create_job(db, job)
        added += 1
    return added



def search_jobs(
    db: Session,
    query=None,
    location=None,
    job_type=None,
    tags=None,
    min_salary=None,
    skip=0,
    limit=20
):
    jobs_query = db.query(Job)

    if query:
        jobs_query = jobs_query.filter(Job.title.ilike(f"%{query}%"))
    
    if location:
        jobs_query = jobs_query.filter(Job.location.ilike(f"%{location}%"))
    
    if job_type:
        jobs_query = jobs_query.filter(Job.job_type.ilike(f"%{job_type}%"))

    if tags:
        tag_list = [tag.strip().lower() for tag in tags.split(",")]
        for tag in tag_list:
            jobs_query = jobs_query.filter(Job.tags.ilike(f"%{tag}%"))


    return jobs_query.offset(skip).limit(limit).all()
