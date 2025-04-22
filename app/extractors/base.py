# app/extractors/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class WebExtractor(ABC):
    """Base abstract class for website content extractors."""
    
    @abstractmethod
    async def extract(self, url: str) -> Dict[str, Any]:
        """Extract content from a website URL.
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        pass