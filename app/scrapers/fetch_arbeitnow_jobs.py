import pprint
import requests
from datetime import datetime, timezone

def fetch_arbeitnow_jobs(search_query: str) -> list[dict]:
    url = "https://www.arbeitnow.com/api/job-board-api"
    headers = {"User-Agent": "JobScraperBot/1.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch jobs: {response.status_code}")
        return []

    jobs_data = response.json()
    jobs = jobs_data.get("data", [])
    print("✅ Successfully fetched Arbeitnow jobs")

    normalized_jobs = []
    for job in jobs:
        title = job.get("title", "").lower()
        if search_query.lower() not in title:
            continue 

        normalized_jobs.append({
            "title": job.get("title"),
            "company_name": job.get("company"),
            "location": job.get("location"),
            "url": job.get("url"),
            "source": "arbeitnow",
            "job_id": f"arbeitnow-{job.get('slug') or job.get('id')}",
            "publication_date": datetime.now(timezone.utc),
            "tags": ", ".join(job.get("tags", [])),  # Safe for DB
            "salary": job.get("salary"),
            "job_type": job.get("type") or None
        })

    return normalized_jobs

# Call with a query string
normalized_jobs = fetch_arbeitnow_jobs("job")
pprint.pprint(normalized_jobs[:30])
