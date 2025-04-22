# app/extractors/factory.py
from enum import Enum
from typing import Dict, Type

from app.extractors.base import WebExtractor
from app.extractors.beautiful_soup_extractor import BeautifulSoupExtractor
from app.extractors.playwright_extractor import PlaywrightExtractor

class ExtractorType(Enum):
    """Enum for available extractor types."""
    BEAUTIFUL_SOUP = "beautiful_soup"
    PLAYWRIGHT = "playwright"

class ExtractorFactory:
    """Factory for creating extractor instances."""
    
    _extractors: Dict[ExtractorType, Type[WebExtractor]] = {
        ExtractorType.BEAUTIFUL_SOUP: BeautifulSoupExtractor,
        ExtractorType.PLAYWRIGHT: PlaywrightExtractor
    }
    
    @classmethod
    def get_extractor(cls, extractor_type: ExtractorType) -> WebExtractor:
        """Get an extractor instance based on the extractor type.
        
        Args:
            extractor_type: The type of extractor to create
            
        Returns:
            An instance of the requested extractor
            
        Raises:
            ValueError: If the extractor type is not supported
        """
        if extractor_type not in cls._extractors:
            raise ValueError(f"Unsupported extractor type: {extractor_type}")
        
        return cls._extractors[extractor_type]()