import sys
import os
from datetime import datetime, timezone
from pprint import pprint
from typing import List

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db.database import SessionLocal
from app.db.crud import create_job
from app.schemas.job import JobCreate
from app.scrapers.fetch_remotive_jobs import fetch_remotive_jobs
from app.scrapers.fetch_remoteok_jobs import fetch_remoteok_jobs
from app.scrapers.fetch_arbeitnow_jobs import fetch_arbeitnow_jobs


def _normalize_datetime_to_utc(dt_obj):
    if dt_obj is None:
        return datetime.min.replace(tzinfo=timezone.utc)
    if dt_obj.tzinfo is None:
        return dt_obj.replace(tzinfo=timezone.utc)
    return dt_obj.astimezone(timezone.utc)


def safe_fetch(fetch_func, source_name, search_query) -> List[dict]:
    try:
        source_jobs = fetch_func(search_query)
        print(f"✅ Successfully fetched {len(source_jobs)} jobs from {source_name}.")
        for job in source_jobs:
            job['publication_date'] = _normalize_datetime_to_utc(job.get('publication_date'))
        return source_jobs
    except Exception as e:
        print(f"❌ Failed to fetch from {source_name}: {e}")
        return []


def aggregate_jobs(search_query="job") -> List[dict]:
    print(f"\n🔎 Starting job aggregation for query: '{search_query}'...")

    jobs = []
    jobs.extend(safe_fetch(fetch_remotive_jobs, "Remotive", search_query))
    jobs.extend(safe_fetch(fetch_remoteok_jobs, "RemoteOK", search_query))
    jobs.extend(safe_fetch(fetch_arbeitnow_jobs, "Arbeitnow", search_query))

    # Deduplicate by job_id
    seen_ids = set()
    unique_jobs = []
    for job in jobs:
        job_id = job.get("job_id")
        if job_id and job_id not in seen_ids:
            seen_ids.add(job_id)
            unique_jobs.append(job)
        elif not job_id:
            print(f"⚠️ Skipping job due to missing 'job_id': {job.get('title')}")

    print(f"\n📦 Total unique jobs fetched: {len(unique_jobs)}")
    return sorted(
        unique_jobs,
        key=lambda j: j.get("publication_date", datetime.min.replace(tzinfo=timezone.utc)),
        reverse=True,
    )


def save_jobs_to_db(jobs: List[dict]):
    db = SessionLocal()
    try:
        new_count = 0
        for job_data in jobs:
            try:
                job_create = JobCreate(**job_data)
                result = create_job(db, job_create)
                if result and (not hasattr(result, "_sa_instance_state") or result.id is None):
                    new_count += 1
            except Exception as e:
                print(f"⚠️ Error saving job {job_data.get('job_id', 'N/A')}: {e}")
        db.commit()
        print(f"✅ Saved {new_count} new jobs to the database.")
    except Exception as e:
        db.rollback()
        print(f"❌ Database error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    search_term = "jobs"  # Customize this as needed
    jobs = aggregate_jobs(search_term)
    if jobs:
        save_jobs_to_db(jobs)
    else:
        print("⚠️ No jobs to save.")

    print("\n--- Sample of fetched jobs (first 20) ---")
    pprint(jobs[:20])
