from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from app.models.business import BusinessDetails

class DatabaseInterface(ABC):
    """Interface for database operations following SOLID principles"""
    
    @abstractmethod
    async def get_company_data(self, company_url: str) -> Optional[BusinessDetails]:
        """Get company data by URL"""
        pass
    
    @abstractmethod
    async def save_company_data(self, company_url: str, data: BusinessDetails) -> bool:
        """Save company data"""
        pass
    
    @abstractmethod
    async def get_question_answer(self, company_url: str, question: str) -> Optional[Dict[str, Any]]:
        """Get cached answer for a question about a company"""
        pass
    
    @abstractmethod
    async def save_question_answer(self, company_url: str, question: str, answer: Dict[str, Any]) -> bool:
        """Save question and answer for a company"""
        pass
    
    @abstractmethod
    async def is_company_scraped(self, company_url: str) -> bool:
        """Check if company data has been scraped"""
        pass 