import pytest
from unittest.mock import patch, MagicMock
from app.services.duckduckgo_search_service import DuckDuckGoSearchService
from typing import Dict, Any, Optional

@pytest.fixture
def mock_ddgs():
    """Fixture to mock the DuckDuckGo search client"""
    with patch('app.services.duckduckgo_search_service.DDGS') as mock:
        yield mock

@pytest.mark.asyncio
async def test_search_web_success(mock_ddgs):
    """Test successful web search"""
    # Mock search results
    mock_results = [
        {
            "title": "Test Result 1",
            "body": "This is a test result",
            "link": "https://example.com/1"
        },
        {
            "title": "Test Result 2",
            "body": "Another test result",
            "link": "https://example.com/2"
        }
    ]
    
    # Configure mock
    mock_instance = MagicMock()
    mock_instance.text.return_value = mock_results
    mock_ddgs.return_value = mock_instance
    
    # Perform search
    results = await DuckDuckGoSearchService.search_web("test query")
    
    # Verify results
    assert results is not None
    assert "results" in results
    assert len(results["results"]) == 2
    assert results["results"][0]["title"] == "Test Result 1"
    assert results["results"][0]["snippet"] == "This is a test result"
    assert results["results"][0]["link"] == "https://example.com/1"
    
    # Verify DDGS was called correctly
    mock_ddgs.assert_called_once()
    mock_instance.text.assert_called_once()

@pytest.mark.asyncio
async def test_search_web_no_results(mock_ddgs):
    """Test search with no results"""
    # Configure mock to return empty list
    mock_instance = MagicMock()
    mock_instance.text.return_value = []
    mock_ddgs.return_value = mock_instance
    
    # Perform search
    results = await DuckDuckGoSearchService.search_web("test query")
    
    # Verify results
    assert results is None

@pytest.mark.asyncio
async def test_search_web_error_handling(mock_ddgs):
    """Test error handling during search"""
    # Configure mock to raise exception
    mock_instance = MagicMock()
    mock_instance.text.side_effect = Exception("Test error")
    mock_ddgs.return_value = mock_instance
    
    # Perform search
    results = await DuckDuckGoSearchService.search_web("test query")
    
    # Verify results
    assert results is None

@pytest.mark.asyncio
async def test_search_web_fallback_parameters(mock_ddgs):
    """Test fallback to different search parameters"""
    # Configure mock to fail first attempt but succeed on second
    mock_instance = MagicMock()
    mock_instance.text.side_effect = [
        Exception("First attempt failed"),
        [
            {
                "title": "Fallback Result",
                "body": "This is a fallback result",
                "link": "https://example.com/fallback"
            }
        ]
    ]
    mock_ddgs.return_value = mock_instance
    
    # Perform search
    results = await DuckDuckGoSearchService.search_web("test query")
    
    # Verify results
    assert results is not None
    assert "results" in results
    assert len(results["results"]) == 1
    assert results["results"][0]["title"] == "Fallback Result"
    
    # Verify DDGS was called multiple times
    assert mock_instance.text.call_count > 1

@pytest.mark.asyncio
async def test_clean_query():
    """Test query cleaning functionality"""
    # Test basic cleaning
    cleaned = DuckDuckGoSearchService._clean_query("  test query?  ")
    assert cleaned == "test query"
    
    # Test product-related query
    cleaned = DuckDuckGoSearchService._clean_query("best product of company")
    assert cleaned == "company best product of company"
    
    # Test with multiple spaces
    cleaned = DuckDuckGoSearchService._clean_query("test    query   with   spaces")
    assert cleaned == "test query with spaces"
    
    # Test with multiple question marks
    cleaned = DuckDuckGoSearchService._clean_query("test query???")
    assert cleaned == "test query" 