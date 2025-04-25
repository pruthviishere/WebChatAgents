"""
Database interface and implementation for WebChatAgents
"""
import json
import os
from typing import Dict, Any, Optional

class DatabaseInterface:
    """Interface for database operations"""
    def save_company_data(self, url: str, data: Dict[str, Any]) -> None:
        """Save company data to the database"""
        raise NotImplementedError

    def get_company_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Get company data from the database"""
        raise NotImplementedError

    def save_answer(self, url: str, question: str, answer: str, confidence: float) -> None:
        """Save question-answer pair to the database"""
        raise NotImplementedError

    def get_answer(self, url: str, question: str) -> Optional[Dict[str, Any]]:
        """Get answer from the database"""
        raise NotImplementedError

class JsonDatabase(DatabaseInterface):
    """JSON file-based database implementation"""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Ensure the database file exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({"companies": {}, "answers": {}}, f)

    def _read_db(self) -> Dict[str, Any]:
        """Read the entire database"""
        with open(self.db_path, 'r') as f:
            return json.load(f)

    def _write_db(self, data: Dict[str, Any]) -> None:
        """Write to the database"""
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)

    def save_company_data(self, url: str, data: Dict[str, Any]) -> None:
        """Save company data to the database"""
        db = self._read_db()
        db["companies"][url] = data
        self._write_db(db)

    def get_company_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Get company data from the database"""
        db = self._read_db()
        return db["companies"].get(url)

    def save_answer(self, url: str, question: str, answer: str, confidence: float) -> None:
        """Save question-answer pair to the database"""
        db = self._read_db()
        if url not in db["answers"]:
            db["answers"][url] = {}
        db["answers"][url][question] = {
            "answer": answer,
            "confidence": confidence
        }
        self._write_db(db)

    def get_answer(self, url: str, question: str) -> Optional[Dict[str, Any]]:
        """Get answer from the database"""
        db = self._read_db()
        return db["answers"].get(url, {}).get(question) 