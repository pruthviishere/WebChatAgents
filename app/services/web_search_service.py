from typing import Dict, Any, Optional
from app.utils.logging import logger
import os
from serpapi import GoogleSearch
import time

class WebSearchService:
    """Service for web search operations using SerpAPI"""
    
    @staticmethod
    async def search_web(query: str) -> Optional[Dict[str, Any]]:
        """Search the web for information related to the query"""
        start_time = time.time()
        try:
            logger.info(f"Starting SerpAPI search for query: {query}")
            
            api_key = os.environ.get("SERPAPI_API_KEY")
            if not api_key:
                logger.error("SERPAPI_API_KEY not found in environment variables")
                return None
            
            # Create search parameters
            params = {
                "engine": "google",
                "q": query,
                "api_key": api_key,
                "num": 5  # Get top 5 results
            }
            
            # Perform search
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract relevant information
            if "organic_results" in results:
                formatted_results = {
                    "results": [
                        {
                            "title": result.get("title", ""),
                            "snippet": result.get("snippet", ""),
                            "link": result.get("link", "")
                        }
                        for result in results["organic_results"]
                    ]
                }
                
                logger.info(f"Successfully retrieved {len(formatted_results['results'])} results from SerpAPI")
                logger.info(f"SerpAPI search completed in {time.time() - start_time:.2f} seconds")
                return formatted_results
            
            logger.warning("No results found in SerpAPI search")
            return None
            
        except Exception as e:
            logger.error(f"Error performing SerpAPI search: {str(e)}")
            return None 