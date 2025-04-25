"""
Test cases for the analyzer router
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.routers.analyzer import WebsiteRequest
from app.utils.database import JsonDatabase
import os
import json

client = TestClient(app)

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

def test_analyze_website_endpoint_with_question(test_db):
    """Test the analyze_website_endpoint with a question"""
    # Test data
    url = "https://example.com"
    question = "What is the company's mission?"
    
    # Mock response data
    mock_data = {
        "url": url,
        "business_details": {
            "mission": "To provide excellent service",
            "products": ["Product A", "Product B"],
            "contact": {
                "email": "contact@example.com",
                "phone": "123-456-7890"
            }
        }
    }
    
    # Save mock data to test database
    test_db.save_company_data(url, mock_data)
    
    # Make request
    response = client.post(
        "/analyze",
        json={"url": url, "question": question}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "confidence" in data
    assert data["answer"] == "To provide excellent service"
    assert 0.8 <= data["confidence"] <= 1.0

def test_analyze_website_endpoint_without_question(test_db):
    """Test the analyze_website_endpoint without a question"""
    # Test data
    url = "https://example.com"
    
    # Mock response data
    mock_data = {
        "url": url,
        "business_details": {
            "mission": "To provide excellent service",
            "products": ["Product A", "Product B"],
            "contact": {
                "email": "contact@example.com",
                "phone": "123-456-7890"
            }
        }
    }
    
    # Save mock data to test database
    test_db.save_company_data(url, mock_data)
    
    # Make request
    response = client.post(
        "/analyze",
        json={"url": url}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "business_details" in data
    assert data["business_details"] == mock_data["business_details"]

def test_analyze_website_endpoint_invalid_url():
    """Test the analyze_website_endpoint with an invalid URL"""
    # Test data
    url = "not-a-url"
    
    # Make request
    response = client.post(
        "/analyze",
        json={"url": url}
    )
    
    # Verify response
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_analyze_website_endpoint_caching(test_db):
    """Test that the analyzer properly caches responses"""
    # Test data
    url = "https://example.com"
    question = "What are the company's products?"
    
    # Mock response data
    mock_data = {
        "url": url,
        "business_details": {
            "mission": "To provide excellent service",
            "products": ["Product A", "Product B"],
            "contact": {
                "email": "contact@example.com",
                "phone": "123-456-7890"
            }
        }
    }
    
    # Save mock data to test database
    test_db.save_company_data(url, mock_data)
    
    # Make first request
    response1 = client.post(
        "/analyze",
        json={"url": url, "question": question}
    )
    
    # Make second request
    response2 = client.post(
        "/analyze",
        json={"url": url, "question": question}
    )
    
    # Verify responses are identical
    assert response1.json() == response2.json() 