import pprint
import requests
from datetime import datetime

def fetch_remotive_jobs(search_query) -> list[dict]:
    url = "https://remotive.com/api/remote-jobs"
    params = {"search": search_query}
    headers = {"User-Agent": "JobScraperBot/1.0"}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch jobs: {response.status_code}")
        return []

    jobs_data = response.json()
    jobs = jobs_data.get("jobs", [])
    print("✅ Successfully fetched Remotive jobs")

    normalized_jobs = []
    for job in jobs:
        normalized_jobs.append({
            "title": job["title"],
            "company_name": job["company_name"],
            "location": job.get("candidate_required_location"),
            "url": job["url"],
            "source": "remotive",
            "job_id": f"remotive-{job['id']}",
            "publication_date": datetime.fromisoformat(job["publication_date"]),
            "tags": job.get("tags", []),
            "salary": job.get("salary"),
            "job_type": job.get("job_type")
        })

    return normalized_jobs
normalized_jobs = fetch_remotive_jobs("job")
pprint.pprint(normalized_jobs[:10])