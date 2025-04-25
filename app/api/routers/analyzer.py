# app/core/analyzer.py
import re
import os
from typing import Dict, Any, Optional
import json
from app.extractors.factory import ExtractorFactory, ExtractorType
from app.models.business import BusinessDetails
from app.core.security import verify_api_key
from app.utils.logging import logger
from fastapi import APIRouter, HTTPException, Depends
from openai import OpenAI
from pydantic import BaseModel, Field
from app.db.json_db import JsonDatabase
from app.services.ai_service import AIService
from app.services.db_service import DatabaseService
from app.services.extractor_service import ExtractorService
from app.models.question import QuestionResponse
from app.services.search_service_factory import SearchServiceFactory
import time

class WebsiteRequest(BaseModel):
    url: str = Field(..., description="Website URL to analyze", example="https://3ds.com")

class QuestionRequest(BaseModel):
    url: str = Field(..., description="Website URL to analyze", example="https://3ds.com")
    question: str = Field(..., description="Question about the company", example="What industry is this company in?")

class QuestionResponse(BaseModel):
    answer: str
    confidence: float
    source: str

class DirectQuestionRequest(BaseModel):
    question: str = Field(..., description="Question to ask the AI", example="What is the capital of France?")
    temperature: float = Field(0.0, description="Temperature for GPT response", ge=0.0, le=1.0)

class DirectQuestionResponse(BaseModel):
    answer: str
    confidence: float = Field(..., description="Confidence score of the answer", ge=0.0, le=1.0)

# Create the router
router = APIRouter(
    prefix="/analyze",
    tags=["analyzer"]
)

# Initialize services
db_service = DatabaseService()

def log_api_call(endpoint: str, request_data: dict, start_time: float, status: str, response_data: dict = None):
    """Log API call details"""
    duration = time.time() - start_time
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "endpoint": endpoint,
        "request": request_data,
        "duration_seconds": round(duration, 2),
        "status": status,
        "response": response_data
    }
    logger.info(f"API Call: {json.dumps(log_entry)}")

def extract_answer_from_business_details(question: str, business_details: BusinessDetails) -> Optional[QuestionResponse]:
    """Extract answer from business details based on question"""
    question = question.lower()
    
    # Industry related questions
    if any(keyword in question for keyword in ["industry", "sector", "business type"]):
        return QuestionResponse(
            answer=business_details.industry.industry,
            confidence=business_details.industry.confidence_score,
            source="industry_data"
        )
    
    # Company size related questions
    if any(keyword in question for keyword in ["size", "employees", "how big", "how many people"]):
        return QuestionResponse(
            answer=business_details.company_size.size_category,
            confidence=business_details.company_size.confidence_score,
            source="company_size_data"
        )
    
    # Location related questions
    if any(keyword in question for keyword in ["location", "headquarters", "where", "based"]):
        return QuestionResponse(
            answer=business_details.location.headquarters,
            confidence=business_details.location.confidence_score,
            source="location_data"
        )
    
    return None

# Original analyzer endpoint
@router.post("/", response_model=BusinessDetails)
async def analyze_website_endpoint(
    request: WebsiteRequest,
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Analyze a website homepage to extract business details.
    """
    start_time = time.time()
    try:
        logger.info(f"Starting website analysis for URL: {request.url}")
        
        # Check if we have cached data
        cached_data = await db_service.get_company_data(request.url)
        if cached_data:
            logger.info(f"Found cached data for URL: {request.url}")
            log_api_call("/analyze", request.dict(), start_time, "success", cached_data.dict())
            return cached_data
        
        logger.info(f"No cached data found, proceeding with extraction for URL: {request.url}")
        
        # Extract website content
        extracted_data = await ExtractorService.extract_website_content(request.url)
        logger.info(f"Successfully extracted content from URL: {request.url}")
        
        # Analyze content
        business_details = await AIService.analyze_website(extracted_data, request.url)
        logger.info(f"Successfully analyzed website content for URL: {request.url}")
        
        # Save the scraped data
        await db_service.save_company_data(request.url, business_details)
        logger.info(f"Saved company data to database for URL: {request.url}")
        
        log_api_call("/analyze", request.dict(), start_time, "success", business_details.dict())
        return business_details
        
    except Exception as e:
        logger.error(f"Error analyzing website: {str(e)}")
        log_api_call("/analyze", request.dict(), start_time, "error", {"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing website: {str(e)}"
        )

# Question endpoint
@router.post("/question", response_model=QuestionResponse)
async def answer_question(
    request: QuestionRequest,
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Answer a specific question about a company.
    """
    start_time = time.time()
    try:
        logger.info(f"Processing question for URL: {request.url}, Question: {request.question}")
        
        # Check if we have a cached answer
        cached_answer = await db_service.get_question_answer(request.url, request.question)
        if cached_answer:
            logger.info(f"Found cached answer for question: {request.question}")
            log_api_call("/analyze/question", request.dict(), start_time, "success", cached_answer.dict())
            return cached_answer
        
        # Get company data (from cache or by scraping)
        company_data = await db_service.get_company_data(request.url)
        if not company_data:
            logger.info(f"No cached company data found, proceeding with extraction for URL: {request.url}")
            # If no cached data, analyze the website
            extracted_data = await ExtractorService.extract_website_content(request.url)
            company_data = await AIService.analyze_website(extracted_data, request.url)
            await db_service.save_company_data(request.url, company_data)
            logger.info(f"Successfully scraped and saved company data for URL: {request.url}")
        
        # Try to answer the question
        answer = AIService.extract_answer_from_business_details(request.question, company_data)
        if not answer:
            logger.info(f"No answer found in scraped data, proceeding with web search for question: {request.question}")
            # If no answer found in scraped data, use web search and LLM
            search_results = await SearchServiceFactory.search_web(request.question)
            if search_results:
                logger.info(f"Found web search results, analyzing with LLM for question: {request.question}")
                # Use LLM to analyze search results and generate answer
                llm_response = await AIService.analyze_with_llm(
                    question=request.question,
                    context=search_results,
                    company_context=company_data.dict() if company_data else None
                )
                
                # Parse LLM response into QuestionResponse format
                answer = QuestionResponse(
                    answer=llm_response.get("answer", ""),
                    confidence=llm_response.get("confidence", 0.0),
                    source="web_search"
                )
                logger.info(f"Successfully generated answer from web search for question: {request.question}")
            else:
                logger.warning(f"No web search results found for question: {request.question}")
                raise HTTPException(
                    status_code=404,
                    detail="Could not find an answer to this question through web search"
                )
        
        # Cache the answer
        await db_service.save_question_answer(request.url, request.question, answer)
        logger.info(f"Saved answer to database for question: {request.question}")
        
        log_api_call("/analyze/question", request.dict(), start_time, "success", answer.dict())
        return answer
        
    except HTTPException:
        log_api_call("/analyze/question", request.dict(), start_time, "error", {"error": "Not found"})
        raise
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        log_api_call("/analyze/question", request.dict(), start_time, "error", {"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail=f"Error answering question: {str(e)}"
        )

@router.post("/direct-question", response_model=DirectQuestionResponse)
async def direct_question(
    request: DirectQuestionRequest,
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Ask a direct question to the GPT model without any context.
    """
    start_time = time.time()
    try:
        logger.info(f"Processing direct question: {request.question}")
        
        # Create a prompt for the GPT model
        prompt = f"""
        You are a helpful AI assistant. Please answer the following question accurately and concisely.
        
        Question: {request.question}
        
        Return your response in JSON format with the following structure:
        {{
            "answer": "Your detailed answer here",
            "confidence": 0.0 to 1.0
        }}
        """
        
        # Call GPT with the prompt
        response_text = await AIService.gpt_call(prompt, temperature=request.temperature)
        response_data = json.loads(response_text)
        
        # Create response object
        answer = DirectQuestionResponse(
            answer=response_data.get("answer", "I couldn't generate an answer."),
            confidence=response_data.get("confidence", 0.0)
        )
        
        log_api_call("/analyze/direct-question", request.dict(), start_time, "success", answer.dict())
        return answer
        
    except Exception as e:
        logger.error(f"Error processing direct question: {str(e)}")
        log_api_call("/analyze/direct-question", request.dict(), start_time, "error", {"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
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
 