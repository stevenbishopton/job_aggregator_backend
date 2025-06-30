from app.celery_config import celery_app
from app.services.aggregator import aggregate_jobs, save_jobs_to_db

@celery_app.task(name="app.tasks.scrape_tasks.scrape_and_store_jobs")
def scrape_and_store_jobs(search_term="job"):
    jobs = aggregate_jobs(search_term)
    if jobs:
        save_jobs_to_db(jobs)
        return f"{len(jobs)} jobs scraped and stored for query: '{search_term}'"
    return "No jobs fetched."
