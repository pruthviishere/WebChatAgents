# app/extractors/playwright_extractor.py
import asyncio
from playwright.async_api import async_playwright
from typing import Dict, Any, Optional
import logging

from app.extractors.base import WebExtractor

logger = logging.getLogger(__name__)

class PlaywrightExtractor(WebExtractor):
    """Website content extractor using Playwright for JS-rendered sites."""
    
    async def extract(self, url: str) -> Dict[str, Any]:
        """Extract content from a website using Playwright.
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set user agent
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                })
                
                # Navigate to the URL
                await page.goto(url, wait_until="networkidle")
                
                # Extract metadata
                title = await page.title()
                
                # Get meta description
                meta_desc = await page.evaluate("""
                    () => {
                        const meta = document.querySelector('meta[name="description"]');
                        return meta ? meta.getAttribute('content') : '';
                    }
                """)
                
                # Get meta keywords
                meta_keywords = await page.evaluate("""
                    () => {
                        const meta = document.querySelector('meta[name="keywords"]');
                        return meta ? meta.getAttribute('content') : '';
                    }
                """)
                
                # Extract text content
                content = await page.evaluate("""
                    () => {
                        // Remove script and style elements
                        const scripts = document.querySelectorAll('script, style');
                        scripts.forEach(s => s.remove());
                        
                        // Get text content
                        return document.body.innerText;
                    }
                """)
                
                await browser.close()
                
                # Limit text length to avoid token limits
                if len(content) > 8000:
                    content = content[:8000]
                
                return {
                    "title": title,
                    "meta_description": meta_desc,
                    "meta_keywords": meta_keywords,
                    "content": content
                }
        
        except Exception as e:
            logger.error(f"Error extracting content from {url} using Playwright: {str(e)}")
            raise

