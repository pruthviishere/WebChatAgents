"""
Test cases for DuckDuckGo search functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.duckduckgo_search_service import DuckDuckGoSearchService

@pytest.mark.asyncio
async def test_search_web():
    """Test the web search functionality"""
    # Mock search results
    mock_results = [
        {
            "title": "Test Company",
            "body": "This is a test company description",
            "link": "https://example.com"
        }
    ]
    
    # Mock the DDGS client
    with patch('app.services.duckduckgo_search_service.DDGS') as mock_ddgs:
        # Configure mock
        mock_instance = MagicMock()
        mock_instance.text.return_value = mock_results
        mock_ddgs.return_value = mock_instance
        
        # Perform search
        results = await DuckDuckGoSearchService.search_web("test company")
        
        # Log the results for debugging
        print("\n=== Search Results ===")
        print(f"Query: test company")
        print(f"Results: {results}")
        print("===================\n")
        
        # Verify results
        assert results is not None
        assert "results" in results
        assert len(results["results"]) == 1
        assert results["results"][0]["title"] == "Test Company"
        assert results["results"][0]["snippet"] == "This is a test company description"
        assert results["results"][0]["link"] == "https://example.com"
        
        # Verify DDGS was called correctly
        mock_ddgs.assert_called_once()
        
        # mock_instance.text.assert_called_once_with(
            # "test company",
            # max_results=5
        # )

@pytest.mark.asyncio
async def test_search_web_no_results():
    """Test search when no results are found"""
    with patch('app.services.duckduckgo_search_service.DDGS') as mock_ddgs:
        # Configure mock to return empty list
        mock_instance = MagicMock()
        mock_instance.text.return_value = []
        mock_ddgs.return_value = mock_instance
        
        # Perform search
        results = await DuckDuckGoSearchService.search_web("nonexistent company")
        
        # Verify results
        assert results is None

@pytest.mark.asyncio
async def test_search_web_error_handling():
    """Test error handling during search"""
    with patch('app.services.duckduckgo_search_service.DDGS') as mock_ddgs:
        # Configure mock to raise exception
        mock_instance = MagicMock()
        mock_instance.text.side_effect = Exception("Search failed")
        mock_ddgs.return_value = mock_instance
        
        # Perform search
        results = await DuckDuckGoSearchService.search_web("test company")
        
        # Verify results
        assert results is None 