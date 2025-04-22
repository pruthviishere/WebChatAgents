# app/core/analyzer.py
import re
from typing import Dict, Any

from app.extractors.factory import ExtractorFactory, ExtractorType
from app.models.business import BusinessDetails
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

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
    
    # Initialize LLM
    llm = ChatOpenAI(
        model_name="gpt-4-turbo",
        temperature=0.2
    )
    
    # Create prompt template
    prompt_template = """
    You are an expert business analyst. Analyze the following website content and extract key business information.
    
    Website Content:
    ```
    {content}
    ```
    
    Website URL: {url}
    
    Extract the following information in a structured format:
    1. Company Name: What is the name of the company?
    2. Industry: What industry does the company belong to? Include a confidence score (0-1) and potential sub-industries.
    3. Company Size: What is the approximate size of the company (small, medium, large) if indicated? Include a confidence score (0-1).
    4. Location: Where is the company headquartered or primarily located? Include a confidence score (0-1).
    5. Description: Provide a brief description of what the company does.
    6. Products/Services: List the main products or services offered by the company.
    7. Technologies: List any technologies mentioned on the website.
    8. Founded Year: When was the company founded (if mentioned)?
    
    For each point, if the information is not available, indicate "Not found" and provide a low confidence score.
    Your response should be in JSON format that matches the following structure:
    {
        "company_name": "string",
        "website_url": "string",
        "industry": {
            "industry": "string",
            "confidence_score": float,
            "sub_industries": ["string"]
        },
        "company_size": {
            "size_category": "string",
            "employee_range": "string",
            "confidence_score": float
        },
        "location": {
            "headquarters": "string",
            "offices": ["string"],
            "countries_of_operation": ["string"],
            "confidence_score": float
        },
        "description": "string",
        "products_services": ["string"],
        "technologies": ["string"],
        "founded_year": integer or null
    }
    """
    
    prompt = PromptTemplate(
        input_variables=["content", "url"],
        template=prompt_template
    )
    
    # Create and run chain
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(content=enriched_content, url=url)
    
    # Parse the result (cleanup JSON and convert to BusinessDetails)
    import json
    import re
    
    # Find JSON content (sometimes LLM adds extra text before/after JSON)
    json_match = re.search(r'({[\s\S]*})', result)
    if json_match:
        result = json_match.group(1)
    
    # Parse JSON into BusinessDetails model
    business_data = json.loads(result)
    return BusinessDetails(**business_data)