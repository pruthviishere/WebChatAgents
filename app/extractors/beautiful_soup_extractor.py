# app/extractors/beautiful_soup_extractor.py
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import logging

from app.extractors.base import WebExtractor

logger = logging.getLogger(__name__)

class BeautifulSoupExtractor(WebExtractor):
    """Website content extractor using BeautifulSoup."""
    
    async def extract(self, url: str) -> Dict[str, Any]:
        """Extract content from a website using BeautifulSoup.
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            # Set a user agent to avoid being blocked
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract metadata
            title = soup.title.string if soup.title else ""
            
            # Get meta description
            meta_desc = ""
            meta_desc_tag = soup.find("meta", attrs={"name": "description"})
            if meta_desc_tag:
                meta_desc = meta_desc_tag.get("content", "")
            
            # Get meta keywords
            meta_keywords = ""
            meta_keywords_tag = soup.find("meta", attrs={"name": "keywords"})
            if meta_keywords_tag:
                meta_keywords = meta_keywords_tag.get("content", "")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text and clean it
            text = soup.get_text()
            # Break into lines and remove leading/trailing space
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Remove blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit text length to avoid token limits
            if len(text) > 8000:
                text = text[:8000]
            
            return {
                "title": title,
                "meta_description": meta_desc,
                "meta_keywords": meta_keywords,
                "content": text
            }
        
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            raise
