from typing import Dict, Any, Optional
from app.services.web_search_service import WebSearchService
from app.services.duckduckgo_search_service import DuckDuckGoSearchService
from app.utils.logging import logger
import time

class SearchServiceFactory:
    """Factory for search services"""
    
    @staticmethod
    def get_search_service(use_duckduckgo: bool = True):
        """Get the appropriate search service"""
        try:
            if use_duckduckgo:
                logger.info("Using DuckDuckGo search service")
                return DuckDuckGoSearchService()
            else:
                logger.info("Using SerpAPI search service")
                return WebSearchService()
        except Exception as e:
            logger.error(f"Error getting search service: {str(e)}")
            raise
    
    @staticmethod
    async def search_web(query: str, use_duckduckgo: bool = True) -> Optional[Dict[str, Any]]:
        """Search the web using the selected service"""
        start_time = time.time()
        try:
            logger.info(f"Starting web search for query: {query}")
            logger.info(f"Using {'DuckDuckGo' if use_duckduckgo else 'SerpAPI'} as search provider")
            
            # Get the appropriate service
            service = SearchServiceFactory.get_search_service(use_duckduckgo)
            
            # Perform search
            results = await service.search_web(query)
            
            # Log search results
            if results:
                logger.info(f"Successfully found {len(results.get('results', []))} search results")
                logger.info(f"Search completed in {time.time() - start_time:.2f} seconds")
            else:
                logger.warning("No search results found")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in search service: {str(e)}")
            # If DuckDuckGo fails and we're using it, try SerpAPI as fallback
            if use_duckduckgo:
                logger.info("DuckDuckGo search failed, trying SerpAPI as fallback")
                try:
                    service = SearchServiceFactory.get_search_service(use_duckduckgo=False)
                    results = await service.search_web(query)
                    if results:
                        logger.info("Successfully retrieved results from SerpAPI fallback")
                        return results
                except Exception as fallback_error:
                    logger.error(f"SerpAPI fallback also failed: {str(fallback_error)}")
            
            return None 