from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, Any, Optional, List
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
