"""
Integration tests for the chat endpoints.
The ClaudeClient is mocked so no real API key is needed.
"""
import pytest
from unittest.mock import AsyncMock, patch


MOCK_REPLY = "Paris is the capital of France."


@pytest.mark.asyncio
async def test_send_message(client):
    with patch(
        "app.services.claude_client.ClaudeClient.complete",
        new_callable=AsyncMock,
        return_value=(MOCK_REPLY, 10, 8),
    ):
        resp = await client.post(
            "/api/v1/chat/",
            json={"session_id": "test-session", "message": "What is the capital of France?"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["reply"] == MOCK_REPLY
    assert data["session_id"] == "test-session"
    assert data["turn"] == 1
    assert data["input_tokens"] == 10


@pytest.mark.asyncio
async def test_conversation_memory(client):
    """Second message in same session should include previous context."""
    with patch(
        "app.services.claude_client.ClaudeClient.complete",
        new_callable=AsyncMock,
        return_value=("It is in Western Europe.", 30, 10),
    ):
        resp = await client.post(
            "/api/v1/chat/",
            json={"session_id": "mem-session", "message": "Where is it located?"},
        )

    assert resp.status_code == 200
    assert resp.json()["turn"] >= 1


@pytest.mark.asyncio
async def test_clear_session(client):
    resp = await client.delete("/api/v1/chat/some-session")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Session cleared"


@pytest.mark.asyncio
async def test_get_session_info(client):
    resp = await client.get("/api/v1/chat/empty-session/history")
    assert resp.status_code == 200
    assert resp.json()["turn_count"] == 0