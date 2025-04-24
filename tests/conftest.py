import pytest
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment"""
    # Set test environment variables
    os.environ["ENVIRONMENT"] = "test"
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    yield
    
    # Cleanup after tests
    # Remove test files and directories
    if os.path.exists("data/test_db.json"):
        os.remove("data/test_db.json")
    if os.path.exists("data") and not os.listdir("data"):
        os.rmdir("data")
    if os.path.exists("logs") and not os.listdir("logs"):
        os.rmdir("logs") 