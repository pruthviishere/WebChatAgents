from typing import Dict, Any, Optional
from app.utils.logging import logger
from duckduckgo_search import DDGS
import time
import re

class DuckDuckGoSearchService:
    """Service for DuckDuckGo search operations"""
    
    @staticmethod
    def _clean_query(query: str) -> str:
        """Clean and format the search query"""
        # Remove extra spaces and question marks
        query = re.sub(r'\s+', ' ', query).strip()
        query = query.rstrip('?')
        
        # Add company name if it's a product-related question
        if any(word in query.lower() for word in ['product', 'service', 'offer', 'provide']):
            # Extract company name from URL if available
            company_name = query.split('of')[-1].strip() if 'of' in query else None
            if company_name:
                query = f"{company_name} {query}"
        
        return query
    
    @staticmethod
    async def search_web(query: str) -> Optional[Dict[str, Any]]:
        """Search the web using DuckDuckGo"""
        start_time = time.time()
        try:
            # Clean and format the query
            cleaned_query = DuckDuckGoSearchService._clean_query(query)
            logger.info(f"Starting DuckDuckGo search for query: {cleaned_query}")
            
            # Initialize DuckDuckGo search with no additional parameters
            ddgs = DDGS()
            
            # Try different search parameters if first attempt fails
            search_params = [
                {"max_results": 5, "safesearch": "moderate"},
                {"max_results": 10, "safesearch": "off"},
                {"max_results": 5, "safesearch": "moderate", "time": "y"}
            ]
            
            for params in search_params:
                try:
                    # Perform search with current parameters
                    results = list(ddgs.text(cleaned_query, **params))
                    
                    if results:
                        formatted_results = {
                            "results": [
                                {
                                    "title": result.get("title", ""),
                                    "snippet": result.get("body", ""),
                                    "link": result.get("link", "")
                                }
                                for result in results
                            ]
                        }
                        
                        logger.info(f"Successfully retrieved {len(results)} results from DuckDuckGo")
                        logger.info(f"DuckDuckGo search completed in {time.time() - start_time:.2f} seconds")
                        return formatted_results
                except Exception as e:
                    logger.warning(f"Search attempt failed with parameters {params}: {str(e)}")
                    continue
            
            # If all attempts fail, try a more general search
            try:
                results = list(ddgs.text(cleaned_query.split('?')[0], max_results=5, safesearch="moderate"))
                if results:
                    formatted_results = {
                        "results": [
                            {
                                "title": result.get("title", ""),
                                "snippet": result.get("body", ""),
                                "link": result.get("link", "")
                            }
                            for result in results
                        ]
                    }
                    logger.info(f"Successfully retrieved {len(results)} results from fallback search")
                    return formatted_results
            except Exception as e:
                logger.warning(f"Fallback search also failed: {str(e)}")
            
            logger.warning(f"No results found in DuckDuckGo search for query: {cleaned_query}")
            return None
            
        except Exception as e:
            logger.error(f"Error performing DuckDuckGo search: {str(e)}")
            return None 