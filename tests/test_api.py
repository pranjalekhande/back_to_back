"""Test the FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from back_to_back.app import create_app


class MockRedis:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self.data = {}
    
    async def setex(self, key: str, ttl: int, value: str):
        self.data[key] = value
    
    async def get(self, key: str):
        return self.data.get(key)
    
    async def delete(self, key: str):
        if key in self.data:
            del self.data[key]
            return 1
        return 0
    
    async def expire(self, key: str, ttl: int):
        return True
    
    async def ping(self):
        return True
    
    async def close(self):
        pass


@pytest.fixture
def client():
    """Create test client with mocked Redis."""
    app = create_app()
    
    # Mock the Redis dependency
    mock_redis = MockRedis()
    app.state.redis = mock_redis
    
    return TestClient(app)


def test_health_check(client):
    """Test basic health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "back-to-back-api"}


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
def test_init_session(client):
    """Test session initialization."""
    payload = {
        "agent_1_persona": "You are a friendly robot who loves technology.",
        "agent_2_persona": "You are a skeptical human who questions everything.",
        "mode": "ai_vs_ai",
        "scenario": "A debate about the future of AI",
        "max_turns": 10
    }
    
    response = client.post("/api/v1/init", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "session_id" in data
    assert data["config"]["mode"] == "ai_vs_ai"
    assert data["status"] == "initialized"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
def test_init_session_minimal(client):
    """Test session initialization with minimal data."""
    payload = {
        "agent_1_persona": "A chef",
        "agent_2_persona": "A food critic"
    }
    
    response = client.post("/api/v1/init", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "session_id" in data
    assert data["config"]["mode"] == "ai_vs_ai"  # Default mode


def test_chat_without_session(client):
    """Test chat endpoint with non-existent session."""
    payload = {
        "session_id": "non-existent-session",
    }
    
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
def test_session_lifecycle(client):
    """Test creating, getting, and deleting a session."""
    # Create session
    payload = {
        "agent_1_persona": "A chef",
        "agent_2_persona": "A food critic"
    }
    
    response = client.post("/api/v1/init", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    session_id = data["session_id"]
    
    # Get session info
    response = client.get(f"/api/v1/session/{session_id}")
    assert response.status_code == 200
    
    session_data = response.json()
    assert session_data["session_id"] == session_id
    assert session_data["current_turn"] == 0
    assert session_data["message_count"] == 0
    
    # Delete session
    response = client.delete(f"/api/v1/session/{session_id}")
    assert response.status_code == 200
    assert response.json()["session_id"] == session_id
    
    # Try to get deleted session
    response = client.get(f"/api/v1/session/{session_id}")
    assert response.status_code == 404


def test_get_session_info_not_found(client):
    """Test getting info for non-existent session."""
    response = client.get("/api/v1/session/non-existent")
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]
