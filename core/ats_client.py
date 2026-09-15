import requests
import re
import html
from config import ATS_PATTERNS

class ATSClient:
    """Client for directly fetching job descriptions from known ATS public APIs."""
    
    @staticmethod
    def identify_ats(url):
        for ats_name, pattern in ATS_PATTERNS.items():
            match = pattern.search(url)
            if match:
                return ats_name, match.groups()
        return None, None

    @staticmethod
    def fetch_job(url):
        """
        Attempts to fetch a job directly from an ATS public API.
        Returns a dict: {"title": str, "company": str, "description": str, "posted_date": str}
        or None if not a recognized ATS or request fails.
        """
        ats_name, groups = ATSClient.identify_ats(url)
        
        if not ats_name:
            return None
            
        try:
            if ats_name == "greenhouse":
                board_token, job_id = groups
                return ATSClient._fetch_greenhouse(board_token, job_id)
            elif ats_name == "lever":
                board_token, job_id = groups
                return ATSClient._fetch_lever(board_token, job_id)
            elif ats_name == "ashby":
                board_token, job_id = groups
                return ATSClient._fetch_ashby(board_token, job_id)
        except Exception:
            return None
            
        return None
        
    @staticmethod
    def _clean_html(raw_html):
        """Removes basic HTML tags and unescapes entities."""
        if not raw_html:
            return ""
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', str(raw_html))
        return html.unescape(cleantext).strip()

    @staticmethod
    def _fetch_greenhouse(board_token, job_id):
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}"
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Decode HTML content
        description = ATSClient._clean_html(data.get('content', ''))
        
        return {
            "title": data.get("title", "Unknown Role"),
            "company": board_token.title().replace("-", " "), # Best guess since API doesn't return company name cleanly
            "description": description,
            "posted_date": data.get("updated_at", "Unknown"),
            "source": "Greenhouse (Free)"
        }

    @staticmethod
    def _fetch_lever(board_token, job_id):
        api_url = f"https://api.lever.co/v0/postings/{board_token}/{job_id}"
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        description = ATSClient._clean_html(data.get('description', '') + "\n" + data.get('descriptionPlain', ''))
        
        return {
            "title": data.get("text", "Unknown Role"),
            "company": board_token.title().replace("-", " "), 
            "description": description,
            "posted_date": data.get("createdAt", "Unknown"),
            "source": "Lever (Free)"
        }

    @staticmethod
    def _fetch_ashby(board_token, job_id):
        # Note: Ashby's public API might require a different structure, but this is a common approximation.
        api_url = f"https://api.ashbyhq.com/posting-api/job-board/{board_token}"
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Ashby often returns a list of jobs, we have to find the one matching the ID
        jobs = data.get("jobs", [])
        target_job = None
        for job in jobs:
            if job.get("id") == job_id:
                target_job = job
                break
                
        if not target_job:
            raise ValueError("Job not found in Ashby board")
            
        return {
            "title": target_job.get("title", "Unknown Role"),
            "company": board_token.title().replace("-", " "), 
            "description": ATSClient._clean_html(target_job.get('descriptionHtml', '')),
            "posted_date": target_job.get("publishedAt", "Unknown"),
            "source": "Ashby (Free)"
        }
