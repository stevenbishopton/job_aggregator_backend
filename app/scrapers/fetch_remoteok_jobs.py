import requests
from datetime import datetime, timezone
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def fetch_remoteok_jobs(search_query: str) -> List[Dict[str, Any]]:
    """
    Fetches jobs from the RemoteOK.com API and normalizes them.
    """
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "JobAggregatorBot/1.0"}
    timeout = 15

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        jobs_data = response.json()

        jobs = [job for job in jobs_data if isinstance(job, dict) and job.get("id")]
        logger.info(f"Successfully fetched {len(jobs)} raw jobs from RemoteOK.")

        normalized_jobs: List[Dict[str, Any]] = []
        for job in jobs:
            try:
                epoch = job.get("epoch")
                if epoch:
                    publication_date = datetime.fromtimestamp(epoch, tz=timezone.utc)
                else:
                    publication_date = datetime.now(timezone.utc)
                    logger.warning(f"RemoteOK job {job.get('id')} missing epoch. Using current UTC.")

                job_id = f"remoteok-{job.get('id')}" if job.get('id') else f"remoteok-{job.get('url') or datetime.now().timestamp()}"


                title = job.get("position") or job.get("title", "")
                if search_query and search_query.lower() not in title.lower():
                    continue

                normalized_jobs.append({
                    "title": title,
                    "company_name": job.get("company"),
                    "location": job.get("location"),
                    "url": job.get("url"),
                    "source": "remoteok",
                    "job_id": job_id,
                    "publication_date": publication_date,
                    "tags": ", ".join(job.get("tags", [])) if isinstance(job.get("tags"), list) else job.get("tags"),
                    "salary": job.get("salary"),
                    "job_type": job.get("type")
                })
            except Exception as e:
                logger.error(f"Error normalizing RemoteOK job {job.get('id', 'N/A')}: {e}", exc_info=True)
                continue

        return normalized_jobs

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching from RemoteOK: {e}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching RemoteOK jobs: {e}", exc_info=True)
        return []

if __name__ == "__main__":
    """
    This block only runs when fetch_remoteok_jobs.py is executed directly.
    It's for testing the scraper in isolation.
    """
    from pprint import pprint
    print("--- Testing RemoteOK Scraper ---")
    jobs = fetch_remoteok_jobs("python")
    pprint(jobs[:5])
    print(f"\nTotal jobs fetched from RemoteOK: {len(jobs)}")