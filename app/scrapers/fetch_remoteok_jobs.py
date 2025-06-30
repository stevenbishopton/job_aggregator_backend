import pprint
import requests
from datetime import datetime, timezone

def fetch_remoteok_jobs(search_query : str) -> list[dict]:
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "JobScraperBot/1.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch jobs from RemoteOK: {response.status_code}")
        return []

    jobs_data = response.json()

    # First item is metadata, skip it
    jobs = [job for job in jobs_data if isinstance(job, dict) and job.get("id")]
    print("✅ Successfully fetched RemoteOK jobs")

    normalized_jobs = []
    for job in jobs:
        try:
            publication_date = datetime.fromtimestamp(job["epoch"])
        except Exception:
            publication_date = datetime.now(timezone.utc)() # type: ignore

        normalized_jobs.append({
            "title": job.get("position") or job.get("title"),
            "company_name": job.get("company"),
            "location": job.get("location"),
            "url": job.get("url"),
            "source": "remoteok",
            "job_id": f"remoteok-{job['id']}",
            "publication_date": publication_date,
            "tags": job.get("tags", []),
            "salary": job.get("salary"),
            "job_type": job.get("type") or None
        })

    return normalized_jobs

# For testing only
if __name__ == "__main__":
    jobs = fetch_remoteok_jobs("job")
    pprint.pprint(jobs[:10])
