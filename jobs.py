import requests, os
from dotenv import load_dotenv

load_dotenv()

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")

def JSearch (job_title : str, city : str):

    url = "https://jsearch.p.rapidapi.com/search"

    querystring = {
        "query":f"{job_title} in {city}",
        "page":"1",
        "num_pages":"1",
        "country":"my",
        "date_posted":"all"
        }

    headers = {
        "x-rapidapi-key": f"{JSEARCH_API_KEY}",
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    results = json_jobs_filter(response.json())
    
    return results
    
    
    
def json_jobs_filter(results):
    return [
        {
            "employer_logo": job.get("employer_logo"),
            "title": job.get("job_title"),
            "location": job.get("job_location"),
            "company": job.get("employer_name"),
            "job_posted": job.get("job_posted_human_readable"),
            "apply_options": job.get("apply_options", [])
        }
        for job in results.get("data", [])
    ]
