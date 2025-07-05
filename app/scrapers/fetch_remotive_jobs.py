import requests
from datetime import datetime, timezone
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def fetch_remotive_jobs(search_query: str) -> List[Dict[str, Any]]:
    """
    Fetches jobs from the Remotive.com API and normalizes them.
    """
    url = "https://remotive.com/api/remote-jobs"
    params = {"search": search_query}
    headers = {"User-Agent": "JobAggregatorBot/1.0"}
    timeout = 15

    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        jobs_data = response.json()
        jobs = jobs_data.get("jobs", [])
        logger.info(f"Successfully fetched {len(jobs)} raw jobs from Remotive.")

        normalized_jobs: List[Dict[str, Any]] = []
        for job in jobs:
            try:
                publication_date_str = job.get("publication_date")
                if publication_date_str:
                    publication_date = datetime.fromisoformat(publication_date_str.replace('Z', '+00:00'))
                    if publication_date.tzinfo is None:
                        publication_date = publication_date.replace(tzinfo=timezone.utc)
                else:
                    publication_date = datetime.now(timezone.utc)
                    logger.warning(f"Remotive job {job.get('id')} missing publication_date. Using current UTC.")

                job_id = f"remotive-{job.get('id')}" if job.get('id') else f"remotive-{job.get('url') or datetime.now().timestamp()}"

                normalized_jobs.append({
                    "title": job.get("title"),
                    "company_name": job.get("company_name"),
                    "location": job.get("candidate_required_location"),
                    "url": job.get("url"),
                    "source": "remotive",
                    "job_id": job_id,
                    "publication_date": publication_date,
                    "tags": ", ".join(job.get("tags", [])) if isinstance(job.get("tags"), list) else job.get("tags"),
                    "salary": job.get("salary"),
                    "job_type": job.get("job_type")
                })
            except Exception as e:
                logger.error(f"Error normalizing Remotive job {job.get('id', 'N/A')}: {e}", exc_info=True)
                continue

        return normalized_jobs

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching from Remotive: {e}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching Remotive jobs: {e}", exc_info=True)
        return []

if __name__ == "__main__":
    """
    This block only runs when fetch_remotive_jobs.py is executed directly.
    It's for testing the scraper in isolation.
    """
    from pprint import pprint
    print("--- Testing Remotive Scraper ---")
    jobs = fetch_remotive_jobs("developer")
    pprint(jobs[:5])
    print(f"\nTotal jobs fetched from Remotive: {len(jobs)}")