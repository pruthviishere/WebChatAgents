from typing import Optional, Dict, Any
from app.models.business import BusinessDetails
from app.models.question import QuestionResponse
from app.db.json_db import JsonDatabase
from app.utils.logging import logger

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self, db_path: str = "data/db.json"):
        self.db = JsonDatabase(db_path)
    
    async def get_company_data(self, company_url: str) -> Optional[BusinessDetails]:
        """Get company data from database"""
        try:
            return await self.db.get_company_data(company_url)
        except Exception as e:
            logger.error(f"Error getting company data: {str(e)}")
            return None
    
    async def save_company_data(self, company_url: str, data: BusinessDetails) -> bool:
        """Save company data to database"""
        try:
            return await self.db.save_company_data(company_url, data)
        except Exception as e:
            logger.error(f"Error saving company data: {str(e)}")
            return False
    
    async def get_question_answer(self, company_url: str, question: str) -> Optional[QuestionResponse]:
        """Get cached answer for a question"""
        try:
            cached_answer = await self.db.get_question_answer(company_url, question)
            if cached_answer:
                return QuestionResponse(**cached_answer)
            return None
        except Exception as e:
            logger.error(f"Error getting question answer: {str(e)}")
            return None
    
    async def save_question_answer(self, company_url: str, question: str, answer: QuestionResponse) -> bool:
        """Save question and answer to database"""
        try:
            return await self.db.save_question_answer(company_url, question, answer.model_dump())
        except Exception as e:
            logger.error(f"Error saving question answer: {str(e)}")
            return False
    
    async def is_company_scraped(self, company_url: str) -> bool:
        """Check if company data exists in database"""
        try:
            return await self.db.is_company_scraped(company_url)
        except Exception as e:
            logger.error(f"Error checking if company is scraped: {str(e)}")
            return False 