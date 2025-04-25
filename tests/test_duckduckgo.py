"""
Simple script to test DuckDuckGo search functionality
"""
from duckduckgo_search import DDGS
import json
import time

def test_search():
    """Test DuckDuckGo search with a simple query"""
    try:
        # Initialize DuckDuckGo search without proxies
        ddgs = DDGS()
        
        # Test query
        query = "test company"
        print(f"\nSearching for: {query}")
        
        # Add a small delay to avoid rate limiting
        time.sleep(1)
        
        # Perform search with basic parameters
        results = list(ddgs.text(
            query,
            max_results=3,
            safesearch="moderate"
        ))
        
        # Print results
        print("\nSearch Results:")
        print(json.dumps(results, indent=2))
        
        if results:
            print("\nSearch successful!")
        else:
            print("\nNo results found.")
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure you have the latest version of duckduckgo-search package")
        print("2. Try running: pip install --upgrade duckduckgo-search")
        print("3. If the issue persists, try using a different version of the package")

if __name__ == "__main__":
    test_search() 