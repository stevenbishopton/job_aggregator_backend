import sys
import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db.database import SessionLocal
from app.db.crud import create_job
from app.schemas.job import JobCreate
from app.scrapers.fetch_remotive_jobs import fetch_remotive_jobs
from app.scrapers.fetch_remoteok_jobs import fetch_remoteok_jobs
from app.scrapers.fetch_arbeitnow_jobs import fetch_arbeitnow_jobs


def _normalize_datetime_to_utc(dt_obj: Any) -> datetime:
    """
    Normalizes a datetime object to UTC.
    Handles None, naive datetimes, and already timezone-aware datetimes.
    """
    if dt_obj is None:
        return datetime.min.replace(tzinfo=timezone.utc)
    if isinstance(dt_obj, str):
        try:
            if 'T' in dt_obj and '+' in dt_obj or 'Z' in dt_obj:
                dt_obj = datetime.fromisoformat(dt_obj.replace('Z', '+00:00'))
            else:
                dt_obj = datetime.strptime(dt_obj.split(' ')[0], '%Y-%m-%d')
        except ValueError:
            logger.warning(f"Could not parse datetime string: {dt_obj}. Using current UTC time.")
            return datetime.now(timezone.utc)
    if not isinstance(dt_obj, datetime):
        logger.warning(f"Invalid datetime object type: {type(dt_obj)}. Using current UTC time.")
        return datetime.now(timezone.utc)

    if dt_obj.tzinfo is None:
        return dt_obj.replace(tzinfo=timezone.utc)
    return dt_obj.astimezone(timezone.utc)


def safe_fetch(fetch_func, source_name: str, search_query: str) -> List[Dict[str, Any]]:
    """
    Safely fetches jobs from a given source, handles exceptions,
    and normalizes publication dates to UTC.
    """
    try:
        source_jobs = fetch_func(search_query)
        logger.info(f"✅ Successfully fetched {len(source_jobs)} jobs from {source_name}.")
        for job in source_jobs:
            job['publication_date'] = _normalize_datetime_to_utc(job.get('publication_date'))
        return source_jobs
    except Exception as e:
        logger.error(f"❌ Failed to fetch from {source_name}: {e}", exc_info=True)
        return []


def aggregate_jobs(search_query: str = "job") -> List[Dict[str, Any]]:
    """
    Aggregates jobs from all defined scrapers.
    """
    logger.info(f"\n🔎 Starting job aggregation for query: '{search_query}'...")

    jobs: List[Dict[str, Any]] = []
    jobs.extend(safe_fetch(fetch_remotive_jobs, "Remotive", search_query))
    jobs.extend(safe_fetch(fetch_remoteok_jobs, "RemoteOK", search_query))
    jobs.extend(safe_fetch(fetch_arbeitnow_jobs, "Arbeitnow", search_query))

    seen_ids = set()
    unique_jobs: List[Dict[str, Any]] = []
    for job in jobs:
        job_id = job.get("job_id")
        if job_id and isinstance(job_id, str) and job_id not in seen_ids:
            seen_ids.add(job_id)
            unique_jobs.append(job)
        elif not job_id:
            logger.warning(f"⚠️ Skipping job due to missing or invalid 'job_id': {job.get('title', 'Unknown Title')}")
        else:
            logger.debug(f"Skipping duplicate job_id: {job_id}")


    logger.info(f"\n📦 Total unique jobs fetched: {len(unique_jobs)}")
    return sorted(
        unique_jobs,
        key=lambda j: j.get("publication_date", datetime.min.replace(tzinfo=timezone.utc)),
        reverse=True,
    )


def save_jobs_to_db(jobs: List[Dict[str, Any]]):
    """
    Saves a list of job dictionaries to the database.
    """
    db = SessionLocal()
    try:
        new_count = 0
        for job_data in jobs:
            try:
                job_create = JobCreate(
                    title=job_data.get('title', 'No Title'),
                    company_name=job_data.get('company_name', 'Unknown Company'),
                    location=job_data.get('location'),
                    url=job_data.get('url', 'No URL'),
                    source=job_data.get('source', 'Unknown'),
                    job_id=job_data.get('job_id', f"manual-{datetime.now().timestamp()}"),
                    publication_date=_normalize_datetime_to_utc(job_data.get('publication_date')),
                    tags=job_data.get('tags'),
                    salary=job_data.get('salary'),
                    job_type=job_data.get('job_type')
                )
                result = create_job(db, job_create)
                if result:
                    new_count += 1
            except Exception as e:
                logger.warning(f"⚠️ Error preparing or saving job {job_data.get('job_id', 'N/A')}: {e}")
        db.commit()
        logger.info(f"✅ Attempted to save {len(jobs)} jobs. Saved {new_count} new jobs to the database.")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Database transaction error: {e}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    """
    This block runs only when aggregator.py is executed directly.
    It's for testing the aggregation logic independently.
    """
    search_term = "engineer"
    jobs = aggregate_jobs(search_term)
    if jobs:
        save_jobs_to_db(jobs)
    else:
        logger.info("⚠️ No jobs to save.")

    logger.info("\n--- Sample of fetched jobs (first 5) ---")
    from pprint import pprint
    pprint(jobs[:5])