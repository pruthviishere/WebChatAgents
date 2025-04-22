# app/main.py
import os
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl
import uvicorn
from typing import Dict, Any, Optional, List
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import logging
from abc import ABC, abstractmethod

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Website Business Analyzer API",
    description="API for extracting key business details from website homepages",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Initialize LLM
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model_name="gpt-4o-mini",
    temperature=0.2
)

# Pydantic Models
class WebsiteRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL of the website to analyze")

class Industry(BaseModel):
    industry: str = Field(..., description="Industry the company belongs to")
    confidence_score: float = Field(..., description="Confidence score for the industry classification")
    sub_industries: Optional[List[str]] = Field(None, description="List of potential sub-industries")

class CompanySize(BaseModel):
    size_category: str = Field(..., description="Size category (small, medium, large)")
    employee_range: Optional[str] = Field(None, description="Approximate employee count range")
    confidence_score: float = Field(..., description="Confidence score for the size estimation")

class Location(BaseModel):
    headquarters: Optional[str] = Field(None, description="Company headquarters location")
    offices: Optional[List[str]] = Field(None, description="List of office locations if available")
    countries_of_operation: Optional[List[str]] = Field(None, description="Countries where the company operates")
    confidence_score: float = Field(..., description="Confidence score for the location information")

class BusinessDetails(BaseModel):
    company_name: str = Field(..., description="Name of the company")
    website_url: HttpUrl = Field(..., description="URL of the analyzed website")
    industry: Industry = Field(..., description="Industry information")
    company_size: CompanySize = Field(..., description="Company size information")
    location: Location = Field(..., description="Location information")
    description: str = Field(..., description="Brief description of the company")
    products_services: List[str] = Field(..., description="List of products or services offered")
    technologies: Optional[List[str]] = Field(None, description="Technologies mentioned on the website")
    founded_year: Optional[int] = Field(None, description="Year the company was founded, if available")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")

# Helper functions
async def verify_api_key(authorization: str = Header(...)):
    """Verify that the correct API key is provided."""
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return True

class Scrapper(ABC):
    @abstractmethod
    async def scrape_website(url: str) -> str:
        pass

class BeautifulSoupScrapper(Scrapper):
    async def scrape_website(url: str) -> str:
        """Scrape the website homepage content."""
        try:
            # Set a user agent to avoid being blocked by websites
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
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
            
            # Extract the company name from title or meta tags
            title = soup.title.string if soup.title else ""
            
            # Get meta description
            meta_desc = ""
            meta_desc_tag = soup.find("meta", attrs={"name": "description"})
            if meta_desc_tag:
                meta_desc = meta_desc_tag.get("content", "")
            
            # Add title and meta description to the top of the text
            enriched_text = f"Title: {title}\nMeta Description: {meta_desc}\n\n{text}"
            
            # Limit text length to avoid token limits
            if len(enriched_text) > 8000:
                enriched_text = enriched_text[:8000]
                
            return enriched_text
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping website {url}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error scraping website: {str(e)}"
            )
class Analyzer(ABC):
    @abstractmethod
    async def analyze_website_content(content: str, url: str) -> BusinessDetails:
        pass
class OpenAIAnalyzer():
    async def analyze_website_content(content: str, url: str) -> BusinessDetails:
        """Use LLM to analyze the website content and extract business details."""
        try:
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
            
            chain = LLMChain(llm=llm, prompt=prompt)
            
            result = chain.run(content=content, url=url)
            
            # Clean up the result and parse JSON
            import json
            # Find JSON content (sometimes LLM adds extra text before/after JSON)
            json_match = re.search(r'({[\s\S]*})', result)
            if json_match:
                result = json_match.group(1)
            
            # Parse JSON into BusinessDetails model
            business_data = json.loads(result)
            return BusinessDetails(**business_data)
            
        except Exception as e:
            logger.error(f"Error analyzing website content: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing website content: {str(e)}"
            )

# API Endpoints
@app.post("/analyze", response_model=BusinessDetails, responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze_website(request: WebsiteRequest, api_key_valid: bool = Depends(verify_api_key)):
    """
    Analyze a website homepage to extract business details.
    
    - **url**: Full URL of the website to analyze (including http:// or https://)
    
    Returns structured business information extracted from the website.
    """
    try:
        # Log request
        logger.info(f"Analyzing website: {request.url}")
        
        # Scrape website content
        beautiful_soup_scrapper:Scrapper = Scrapper(BeautifulSoupScrapper)
        content = await beautiful_soup_scrapper.scrape_website(str(request.url))
        
        # Analyze content with LLM
        open_ai_analyser: Analyzer = Analyzer(OpenAIAnalyzer())
        business_details = await open_ai_analyser.analyze_website_content(content, str(request.url))
        
        return business_details
        
    except Exception as e:
        logger.error(f"Error analyzing website: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing website: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)