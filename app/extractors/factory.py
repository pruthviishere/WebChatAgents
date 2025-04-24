# app/extractors/factory.py
from enum import Enum
from typing import Dict, Type

from app.extractors.base import WebExtractor
from app.extractors.beautiful_soup_extractor import BeautifulSoupExtractor
from app.extractors.playwright_extractor import PlaywrightExtractor


from enum import Enum
from typing import Any
from bs4 import BeautifulSoup
import requests
from playwright.async_api import async_playwright
from abc import ABC, abstractmethod

class ExtractorType(Enum):
    BEAUTIFUL_SOUP = "beautiful_soup"
    PLAYWRIGHT = "playwright"

class BaseExtractor(ABC):
    @abstractmethod
    async def extract(self, url: str) -> dict:
        pass

class ExtractorType(Enum):
    """Enum for available extractor types."""
    BEAUTIFUL_SOUP = "beautiful_soup"
    PLAYWRIGHT = "playwright"

class ExtractorFactory:
    @staticmethod
    def create_extractor(extractor_type: ExtractorType) -> BaseExtractor:
        if extractor_type == ExtractorType.BEAUTIFUL_SOUP:
            return BeautifulSoupExtractor()
        elif extractor_type == ExtractorType.PLAYWRIGHT:
            return PlaywrightExtractor()
        else:
            raise ValueError(f"Unknown extractor type: {extractor_type}")
class ExtractorFactordy:
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