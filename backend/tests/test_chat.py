import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_chat_valid_message():
    """Test POST /api/chat with valid message returns mock response."""
    payload = {
        "message": "Hello, Sovereign AI Workbench!",
        "conversation_id": "test-session-123"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str) and len(data["answer"]) > 0
    assert data["conversation_id"] == "test-session-123"
    assert "sources" in data
    assert isinstance(data["sources"], list)


@pytest.mark.asyncio
async def test_chat_empty_message():
    """Test POST /api/chat with empty or whitespace message returns 422 error."""
    payload = {
        "message": "   "
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
