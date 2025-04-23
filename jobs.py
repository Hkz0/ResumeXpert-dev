from serpapi import GoogleSearch
from dotenv import load_dotenv
import os


load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")


def job_listings(job_title: str, city: str):
    
    # serpapi parameters
    params = {
        "engine": "google_jobs",
        "q": f"{job_title} in {city}",
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }
    
    search = GoogleSearch(params)
    results = json_jobs_filter(search.get_dict())
    
    return results

def json_jobs_filter (results):
    jobs_list = []
    
    for job in results.get("jobs_results", []):
        job_data = {
            "title": job.get("title"),
            "location": job.get("location"),
            "company": job.get("company_name"),
            "description": job.get("description", "")[:300] + "...",  
            "apply_options": job.get("apply_options", [])  
        }
        jobs_list.append(job_data)
    
    
    
    return jobs_list
    