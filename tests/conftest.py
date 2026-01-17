import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def fresh_activities(monkeypatch):
    """Provide fresh activities data for each test"""
    from app import activities
    
    # Store original activities
    original = {k: {"participants": list(v["participants"])} for k, v in activities.items()}
    
    yield activities
    
    # Restore original state after test
    for key, value in activities.items():
        value["participants"] = original[key]["participants"]
