"""
Test cases for the database module
"""
import pytest
import os
import json
from app.utils.database import JsonDatabase

@pytest.fixture
def test_db():
    """Fixture to create a test database"""
    db_path = "data/test_db.json"
    os.makedirs("data", exist_ok=True)
    db = JsonDatabase(db_path)
    yield db
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists("data") and not os.listdir("data"):
        os.rmdir("data")

def test_save_and_get_company_data(test_db):
    """Test saving and retrieving company data"""
    # Test data
    url = "https://example.com"
    data = {
        "url": url,
        "business_details": {
            "mission": "Test mission",
            "products": ["Product A", "Product B"]
        }
    }
    
    # Save data
    test_db.save_company_data(url, data)
    
    # Retrieve data
    retrieved_data = test_db.get_company_data(url)
    
    # Verify
    assert retrieved_data == data

def test_save_and_get_answer(test_db):
    """Test saving and retrieving answers"""
    # Test data
    url = "https://example.com"
    question = "What is the company's mission?"
    answer = "Test mission"
    confidence = 0.9
    
    # Save answer
    test_db.save_answer(url, question, answer, confidence)
    
    # Retrieve answer
    retrieved_answer = test_db.get_answer(url, question)
    
    # Verify
    assert retrieved_answer is not None
    assert retrieved_answer["answer"] == answer
    assert retrieved_answer["confidence"] == confidence

def test_get_nonexistent_data(test_db):
    """Test retrieving nonexistent data"""
    # Test data
    url = "https://nonexistent.com"
    question = "What is the company's mission?"
    
    # Retrieve data
    company_data = test_db.get_company_data(url)
    answer = test_db.get_answer(url, question)
    
    # Verify
    assert company_data is None
    assert answer is None

def test_database_persistence(test_db):
    """Test that data persists between database instances"""
    # Test data
    url = "https://example.com"
    data = {
        "url": url,
        "business_details": {
            "mission": "Test mission"
        }
    }
    
    # Save data
    test_db.save_company_data(url, data)
    
    # Create new database instance
    new_db = JsonDatabase("data/test_db.json")
    
    # Retrieve data
    retrieved_data = new_db.get_company_data(url)
    
    # Verify
    assert retrieved_data == data 