from typing import Dict, Any
from app.extractors.factory import ExtractorFactory, ExtractorType
from app.utils.logging import logger
import re

class ExtractorService:
    """Service for website extraction operations"""
    
    @staticmethod
    async def select_best_extractor(url: str) -> ExtractorType:
        """Select the best extractor for a given URL"""
        # Check for common SPAs and JS-heavy websites
        spa_patterns = [
            r'react', r'vue', r'angular', r'svelte', r'next\.js', r'nuxt'
        ]
        
        # Check for common e-commerce platforms
        ecommerce_patterns = [
            r'shopify', r'magento', r'woocommerce', r'bigcommerce'
        ]
        
        # Default to BeautifulSoup for most sites
        extractor_type = ExtractorType.BEAUTIFUL_SOUP
        
        # For SPAs and complex JS sites, use Playwright
        for pattern in spa_patterns + ecommerce_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                extractor_type = ExtractorType.PLAYWRIGHT
                break
        
        logger.info(f"Selected extractor {extractor_type.value} for URL: {url}")
        return extractor_type
    
    @staticmethod
    async def extract_website_content(url: str) -> Dict[str, Any]:
        """Extract content from a website"""
        try:
            # Select best extractor
            extractor_type = await ExtractorService.select_best_extractor(url)
            
            # Create extractor instance
            extractor = ExtractorFactory.create_extractor(extractor_type)
            
            # Extract content
            return await extractor.extract(url)
        except Exception as e:
            logger.error(f"Error extracting website content: {str(e)}")
            raise 