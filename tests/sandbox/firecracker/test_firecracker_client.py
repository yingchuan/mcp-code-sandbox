# tests/sandbox/firecracker/test_firecracker_client.py
"""
Tests for the FirecrackerClient class.
These tests use pytest fixtures and mocks to test the client without making actual HTTP requests.
"""
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

# imports
from src.sandbox.firecracker.firecracker_client import FirecrackerClient


@pytest.fixture
def mock_httpx_client():
    """Fixture to create a mock httpx async client."""
    with patch('httpx.AsyncClient', autospec=True) as mock:
        yield mock


@pytest.fixture
def client():
    """Fixture to create a FirecrackerClient instance."""
    return FirecrackerClient(backend_url="http://test-server.example.com", api_key="test-api-key")


@pytest.mark.asyncio
async def test_init():
    """Test initialization of FirecrackerClient."""
    client = FirecrackerClient(backend_url="http://test-server.example.com", api_key="test-api-key")
    assert client.backend_url == "http://test-server.example.com"
    assert client.api_key == "test-api-key"
    assert client.session is None


@pytest.mark.asyncio
async def test_ensure_session(client, mock_httpx_client):
    """Test _ensure_session creates a session with correct headers."""
    await client._ensure_session()
    mock_httpx_client.assert_called_once()
    assert client.session is not None


@pytest.mark.asyncio
async def test_close(client):
    """Test close method properly closes the session."""
    # Setup mock session
    mock_session = AsyncMock()
    mock_session.aclose = AsyncMock()
    client.session = mock_session
    
    await client.close()
    mock_session.aclose.assert_called_once()
    assert client.session is None


@pytest.mark.asyncio
async def test_spawn_microvm(client):
    """Test spawn_microvm method makes correct request and returns expected response."""
    # Set up mock session and response
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = MagicMock(return_value={"microvm_id": "test-vm-123"})
    
    client.session = AsyncMock()
    client.session.post = AsyncMock(return_value=mock_response)
    
    # Call method and check results
    result = await client.spawn_microvm()
    assert result == {"microvm_id": "test-vm-123"}
    client.session.post.assert_called_once_with("http://test-server.example.com/microvm/spawn")


@pytest.mark.asyncio
async def test_shutdown_microvm(client):
    """Test shutdown_microvm method makes correct request with expected payload."""
    # Set up mock session and response
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = MagicMock(return_value={"success": True})
    
    client.session = AsyncMock()
    client.session.post = AsyncMock(return_value=mock_response)
    
    # Call method and check results
    result = await client.shutdown_microvm("test-vm-123")
    assert result == {"success": True}
    client.session.post.assert_called_once_with(
        "http://test-server.example.com/microvm/shutdown",
        json={"microvm_id": "test-vm-123"}
    )


@pytest.mark.asyncio
async def test_run_code(client):
    """Test run_code method makes correct request with expected payload."""
    # Set up mock session and response
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    
    client.session = AsyncMock()
    client.session.post = AsyncMock(return_value=mock_response)
    
    # Setup payload
    payload = {
        "microvm_id": "test-vm-123",
        "code": "print('hello world')"
    }
    
    # Call method and check results
    result = await client.run_code(payload)
    assert result == mock_response
    client.session.post.assert_called_once_with(
        "http://test-server.example.com/microvm/run_code",
        json=payload
    )


@pytest.mark.asyncio
async def test_run_command(client):
    """Test run_command method makes correct request with expected payload."""
    # Set up mock session and response
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    
    client.session = AsyncMock()
    client.session.post = AsyncMock(return_value=mock_response)
    
    # Setup payload
    payload = {
        "microvm_id": "test-vm-123",
        "command": "ls -la"
    }
    
    # Call method and check results
    result = await client.run_command(payload)
    assert result == mock_response
    client.session.post.assert_called_once_with(
        "http://test-server.example.com/microvm/run_command",
        json=payload
    )


@pytest.mark.asyncio
async def test_list_microvms(client):
    """Test list_microvms method makes correct request."""
    # Set up mock session and response
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = MagicMock(return_value=[{"microvm_id": "test-vm-123"}, {"microvm_id": "test-vm-456"}])
    
    client.session = AsyncMock()
    client.session.get = AsyncMock(return_value=mock_response)
    
    # Call method and check results
    result = await client.list_microvms()
    assert result == [{"microvm_id": "test-vm-123"}, {"microvm_id": "test-vm-456"}]
    client.session.get.assert_called_once_with("http://test-server.example.com/microvm/list")


@pytest.mark.asyncio
async def test_get_microvm_status(client):
    """Test get_microvm_status method makes correct request with expected params."""
    # Set up mock session and response
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = MagicMock(return_value={"microvm_id": "test-vm-123", "status": "running"})
    
    client.session = AsyncMock()
    client.session.get = AsyncMock(return_value=mock_response)
    
    # Call method and check results
    result = await client.get_microvm_status("test-vm-123")
    assert result == {"microvm_id": "test-vm-123", "status": "running"}
    client.session.get.assert_called_once_with(
        "http://test-server.example.com/microvm/status",
        params={"microvm_id": "test-vm-123"}
    )


@pytest.mark.asyncio
async def test_error_handling(client):
    """Test that exceptions from the HTTP request are properly raised."""
    # Set up session to raise an exception
    client.session = AsyncMock()
    client.session.post = AsyncMock(side_effect=httpx.HTTPStatusError(
        "Error", request=MagicMock(), response=MagicMock()))
    
    # Verify exception is raised
    with pytest.raises(httpx.HTTPStatusError):
        await client.spawn_microvm()