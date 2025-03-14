# tests/conftest.py
"""
Global pytest fixtures and configuration.
"""
import os
import sys
import pytest

# Add parent directory to the Python path to make imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Global fixtures can be defined here
@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Set up logging for tests."""
    import logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Lower the log level for tests
    logging.getLogger().setLevel(logging.ERROR)
    
    # You can adjust specific loggers as needed
    # Example: logging.getLogger("sandbox").setLevel(logging.DEBUG)
    
    yield  # This is where the testing happens
    
    # Any teardown after all tests complete