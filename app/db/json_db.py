import json
import os
from typing import Optional, Dict, Any
from app.models.business import BusinessDetails
from app.db.interfaces import DatabaseInterface
from app.utils.logging import logger

class JsonDatabase(DatabaseInterface):
    """JSON file-based database implementation"""
    
    def __init__(self, db_path: str = "data/db.json"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file and directory exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            self._save_db({
                "companies": {},
                "questions": {}
            })
    
    def _load_db(self) -> Dict[str, Any]:
        """Load database from file"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading database: {str(e)}")
            return {"companies": {}, "questions": {}}
    
    def _save_db(self, data: Dict[str, Any]):
        """Save database to file"""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving database: {str(e)}")
    
    async def get_company_data(self, company_url: str) -> Optional[BusinessDetails]:
        """Get company data by URL"""
        db = self._load_db()
        company_data = db["companies"].get(company_url)
        if company_data:
            return BusinessDetails(**company_data)
        return None
    
    async def save_company_data(self, company_url: str, data: BusinessDetails) -> bool:
        """Save company data"""
        try:
            db = self._load_db()
            db["companies"][company_url] = data.model_dump()
            self._save_db(db)
            return True
        except Exception as e:
            logger.error(f"Error saving company data: {str(e)}")
            return False
    
    async def get_question_answer(self, company_url: str, question: str) -> Optional[Dict[str, Any]]:
        """Get cached answer for a question about a company"""
        db = self._load_db()
        company_questions = db["questions"].get(company_url, {})
        return company_questions.get(question)
    
    async def save_question_answer(self, company_url: str, question: str, answer: Dict[str, Any]) -> bool:
        """Save question and answer for a company"""
        try:
            db = self._load_db()
            if company_url not in db["questions"]:
                db["questions"][company_url] = {}
            db["questions"][company_url][question] = answer
            self._save_db(db)
            return True
        except Exception as e:
            logger.error(f"Error saving question answer: {str(e)}")
            return False
    
    async def is_company_scraped(self, company_url: str) -> bool:
        """Check if company data has been scraped"""
        db = self._load_db()
        return company_url in db["companies"] 