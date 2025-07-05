import pprint
import requests
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def fetch_arbeitnow_jobs(search_query: str) -> list[dict]:
    url = "https://www.arbeitnow.com/api/job-board-api"
    headers = {"User-Agent": "JobScraperBot/1.0"}
    timeout = 15

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        jobs_data = response.json()
        jobs = jobs_data.get("data", [])
        logger.info(f"Successfully fetched {len(jobs)} raw jobs from Arbeitnow.")

        normalized_jobs = []
        for job in jobs:
            title = job.get("title", "").lower()
            if search_query and search_query.lower() not in title:
                continue

            created_at_epoch = job.get("created_at")
            if created_at_epoch:
                publication_date = datetime.fromtimestamp(created_at_epoch, tz=timezone.utc)
            else:
                publication_date = datetime.now(timezone.utc)
                logger.warning(f"Arbeitnow job {job.get('slug')} missing created_at. Using current UTC.")

            job_id = f"arbeitnow-{job.get('slug') or job.get('id') or datetime.now().timestamp()}"

            normalized_jobs.append({
                "title": job.get("title"),
                "company_name": job.get("company"),
                "location": job.get("location"),
                "url": job.get("url"),
                "source": "arbeitnow",
                "job_id": job_id,
                "publication_date": publication_date,
                "tags": ", ".join(job.get("tags", [])),
                "salary": job.get("salary_range") or job.get("salary"),
                "job_type": job.get("job_type") or job.get("type")
            })

        return normalized_jobs

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching from Arbeitnow: {e}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching Arbeitnow jobs: {e}", exc_info=True)
        return []

if __name__ == "__main__":
    print("--- Testing Arbeitnow Scraper ---")
    test_search_query = "developer"
    normalized_jobs = fetch_arbeitnow_jobs(test_search_query)
    pprint.pprint(normalized_jobs[:5])
    print(f"\nTotal jobs fetched from Arbeitnow (for '{test_search_query}'): {len(normalized_jobs)}")