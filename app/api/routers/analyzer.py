# app/core/analyzer.py
import re
import os
from typing import Dict, Any
import json
from app.extractors.factory import ExtractorFactory, ExtractorType
from app.models.business import BusinessDetails
from app.core.security import verify_api_key
from app.utils.logging import logger
from fastapi import APIRouter, HTTPException, Depends
from openai import OpenAI
from pydantic import BaseModel, Field

class WebsiteRequest(BaseModel):
    url: str = Field(..., description="Website URL to analyze", example="https://3ds.com")

# Create the router
router = APIRouter(
    prefix="/analyze",
    tags=["analyzer"]
)

# Add the endpoint
@router.post("/", response_model=BusinessDetails)
async def analyze_website_endpoint(
    request: WebsiteRequest,
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Analyze a website homepage to extract business details.
    """
    try:
        # Select best extractor
        extractor_type = await select_best_extractor(str(request.url))
        
        # Create extractor instance
        extractor = ExtractorFactory.create_extractor(extractor_type)
        
        # Extract content
        extracted_data = await extractor.extract(str(request.url))
        
        # Analyze content
        business_details = await analyze_website(extracted_data, str(request.url))
        
        return business_details
        
    except Exception as e:
        logger.error(f"Error analyzing website: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing website: {str(e)}"
        )
    
async def select_best_extractor(url: str) -> ExtractorType:
    """Select the best extractor for a given URL.
    
    Args:
        url: The URL to analyze
        
    Returns:
        The most appropriate extractor type for the URL
    """
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

async def analyze_website(extracted_data: Dict[str, Any], url: str) -> BusinessDetails:
    """Analyze website content to extract business details.
    
    Args:
        extracted_data: Dictionary containing extracted website content
        url: The URL of the website
        
    Returns:
        BusinessDetails object with extracted business information
    """
    # Prepare content for LLM analysis
    title = extracted_data.get("title", "")
    meta_description = extracted_data.get("meta_description", "")
    meta_keywords = extracted_data.get("meta_keywords", "")
    content = extracted_data.get("content", "")
    
    # Create enriched content with metadata
    enriched_content = (
        f"Title: {title}\n"
        f"Meta Description: {meta_description}\n"
        f"Meta Keywords: {meta_keywords}\n\n"
        f"Content:\n{content}"
    )
    return call_llm(enriched_content,url)

def gpt_call(prompt: str, temperature: float = 0.0) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that provides information in JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperature,
        response_format={"type": "json_object"}  # Correct parameter placement
    )
    
    response_content = response.choices[0].message.content.strip()
    print(f"Raw response: {response_content}")
    return response_content

def call_llm(enriched_content, url) -> BusinessDetails:
    # Generate the schema
    schema = BusinessDetails.model_json_schema()
    prompt = f"""
    You are an expert business analyst. Analyze the following website content and extract key business information.
    Website Content:
    {enriched_content}
    Website URL: {url}
    Return the results in JSON format with the following structure:
    {schema}
    """

    try:
        response_text = gpt_call(prompt)
        business_data = BusinessDetails.parse_raw(response_text)
        return business_data
    except Exception as e:
        print(f"Error processing response: {e}")
        print(f"Response text: {response_text}")
        # Return a default object to prevent crashes
        return BusinessDetails()
 