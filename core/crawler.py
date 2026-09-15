import requests
import json
import time

class CrawlerClient:
    """Client for interacting with Firecrawl to scrape web pages and search for jobs."""
    
    BASE_URL = "https://api.firecrawl.dev/v1"
    
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Firecrawl API key is required.")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def scrape_url(self, url):
        """
        Scrapes a given URL and extracts the markdown content using Firecrawl.
        """
        endpoint = f"{self.BASE_URL}/scrape"
        payload = {
            "url": url,
            "formats": ["markdown"]
        }
        
        try:
            resp = requests.post(endpoint, headers=self.headers, json=payload, timeout=30)
            
            # Better error handling for non-technical users
            if resp.status_code == 401:
                raise ValueError("Invalid Firecrawl API Key. Please check your key and try again.")
            elif resp.status_code == 429:
                raise ValueError("Firecrawl rate limit exceeded. You are out of credits or making requests too fast.")
                
            resp.raise_for_status()
            data = resp.json()
            
            if not data.get("success"):
                raise ValueError(f"Firecrawl failed to scrape: {data.get('error', 'Unknown error')}")
                
            md_content = data.get("data", {}).get("markdown", "")
            metadata = data.get("data", {}).get("metadata", {})
            
            return {
                "title": metadata.get("title", "Unknown Role"),
                "company": "Extracted from Web", # Heuristic fallback
                "description": md_content,
                "posted_date": "Recent",
                "source": "Firecrawl Web Scraper"
            }
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Network error while contacting Firecrawl: {str(e)}")

    def search_jobs(self, query):
        """
        Uses Firecrawl's search functionality (if available, otherwise we use scrape on search engine results)
        Since Firecrawl search might require specific endpoints, we simulate a standard approach.
        """
        # Note: Actual Firecrawl search API is at /v1/search (requires search credits).
        endpoint = f"{self.BASE_URL}/search"
        payload = {
            "query": query,
            "limit": 3
        }
        
        try:
            resp = requests.post(endpoint, headers=self.headers, json=payload, timeout=30)
            
            if resp.status_code == 401:
                raise ValueError("Invalid Firecrawl API Key. Please check your key and try again.")
            
            resp.raise_for_status()
            data = resp.json()
            
            if not data.get("success"):
                raise ValueError(f"Search failed: {data.get('error', 'Unknown error')}")
                
            results = []
            for item in data.get("data", []):
                results.append({
                    "url": item.get("url"),
                    "title": item.get("title", "Unknown Title"),
                    "snippet": item.get("description", "")
                })
            return results
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Network error while searching: {str(e)}")
