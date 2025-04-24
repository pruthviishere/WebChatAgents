# crew4ai_extractor.py

import os
import json
import aiohttp
 
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.extractors.base import WebExtractor
from app.utils.logging import logger

class Crew4AIExtractor(WebExtractor):
    """Implementation of WebExtractor using Crew4AI's web scraping capabilities."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Crew4AI extractor.
        
        Args:
            api_key: Crew4AI API key. If not provided, will look for CREW4AI_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("CREW4AI_API_KEY")
        if not self.api_key:
            raise ValueError("Crew4AI API key is required either as a parameter or as CREW4AI_API_KEY environment variable")
        
        self.base_url = "https://api.crew4ai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def extract(self, url: str) -> Dict[str, Any]:
        """Extract content from a website URL using Crew4AI.
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        async with aiohttp.ClientSession() as session:
            # Start a scraping job
            scrape_job = await self._start_scrape_job(session, url)
            job_id = scrape_job.get("job_id")
            
            if not job_id:
                raise ValueError(f"Failed to start scraping job: {scrape_job}")
            
            # Poll for job completion
            result = await self._poll_job_status(session, job_id)
            
            # Process and return the results
            return self._process_results(result, url)
    
    async def _start_scrape_job(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Start a new scraping job on Crew4AI.
        
        Args:
            session: Active aiohttp ClientSession
            url: URL to scrape
            
        Returns:
            Job information including job_id
        """
        payload = {
            "url": url,
            "extraction_type": "full_page",  # Options: full_page, main_content, custom
            "include_metadata": True,
            "include_images": True,
            "include_links": True
        }
        
        async with session.post(
            f"{self.base_url}/scrape", 
            headers=self.headers,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise ValueError(f"Failed to start scrape job: {error_text}")
            
            return await response.json()
    
    async def _poll_job_status(self, session: aiohttp.ClientSession, job_id: str, 
                               max_attempts: int = 30, delay: int = 2) -> Dict[str, Any]:
        """Poll for job completion.
        
        Args:
            session: Active aiohttp ClientSession
            job_id: Job ID to poll
            max_attempts: Maximum number of polling attempts
            delay: Delay between polling attempts in seconds
            
        Returns:
            Job results when complete
        """
        import asyncio
        
        for _ in range(max_attempts):
            async with session.get(
                f"{self.base_url}/jobs/{job_id}", 
                headers=self.headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"Failed to check job status: {error_text}")
                
                result = await response.json()
                status = result.get("status")
                
                if status == "completed":
                    return result
                elif status == "failed":
                    raise ValueError(f"Scraping job failed: {result.get('error')}")
                
                # Wait before polling again
                await asyncio.sleep(delay)
        
        raise TimeoutError(f"Job {job_id} did not complete within the timeout period")
    
    def _process_results(self, job_result: Dict[str, Any], original_url: str) -> Dict[str, Any]:
        """Process and format the job results.
        
        Args:
            job_result: Raw job result from Crew4AI
            original_url: The original URL that was scraped
            
        Returns:
            Processed content and metadata
        """
        data = job_result.get("data", {})
        
        return {
            "url": original_url,
            "title": data.get("title", ""),
            "content": data.get("content", ""),
            "text_content": data.get("text_content", ""),
            "html": data.get("html", ""),
            "metadata": {
                "description": data.get("description", ""),
                "keywords": data.get("keywords", []),
                "language": data.get("language", ""),
                "author": data.get("author", ""),
                "published_date": data.get("published_date", ""),
                "favicon": data.get("favicon", "")
            },
            "links": data.get("links", []),
            "images": data.get("images", []),
            "scrape_time": job_result.get("completed_at", "")
        }
