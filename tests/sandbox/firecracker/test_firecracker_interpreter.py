# tests/src.sandbox/firecracker/test_firecracker_interpreter.py
"""
Tests for the FirecrackerInterpreter class.
These tests use pytest fixtures and mocks to test the interpreter without making actual HTTP requests.
"""
import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock

from src.sandbox.firecracker.firecracker_interpreter import FirecrackerInterpreter
from src.sandbox.code_interpreter import ExecutionResult

# Filter out coroutine warnings for the entire module
pytestmark = [
    pytest.mark.filterwarnings("ignore::RuntimeWarning")
]


@pytest.fixture
def mock_client():
    """Fixture to create a mock FirecrackerClient."""
    with patch('src.sandbox.firecracker.firecracker_interpreter.FirecrackerClient') as mock:
        client_instance = mock.return_value
        client_instance.spawn_microvm = AsyncMock(return_value={"microvm_id": "test-vm-123"})
        client_instance.shutdown_microvm = AsyncMock(return_value={"success": True})
        client_instance.close = AsyncMock()
        
        # Configure run_code and run_command responses
        mock_code_response = MagicMock()
        mock_code_response.json = MagicMock(return_value={
            "result": {
                "stdout": "code output",
                "stderr": ""
            }
        })
        client_instance.run_code = AsyncMock(return_value=mock_code_response)
        
        mock_command_response = MagicMock()
        mock_command_response.json = MagicMock(return_value={
            "result": {
                "stdout": "command output",
                "stderr": ""
            }
        })
        client_instance.run_command = AsyncMock(return_value=mock_command_response)
        
        yield mock


@pytest.fixture
def mock_file_interface():
    """Fixture to create a mock FirecrackerFileInterface."""
    with patch('src.sandbox.firecracker.firecracker_interpreter.FirecrackerFileInterface') as mock:
        yield mock


@pytest.fixture
def interpreter(mock_client, mock_file_interface):
    """Fixture to create a FirecrackerInterpreter instance with mocked dependencies."""
    interpreter = FirecrackerInterpreter(backend_url="http://test-server.example.com", api_key="test-api-key")
    return interpreter


@pytest.mark.asyncio
async def test_init_with_direct_values():
    """Test initialization with directly provided values."""
    interpreter = FirecrackerInterpreter(backend_url="http://test-server.example.com", api_key="test-api-key")
    assert interpreter.backend_url == "http://test-server.example.com"
    assert interpreter.api_key == "test-api-key"
    assert interpreter._initialized is False
    assert interpreter.microvm_id is None


@pytest.mark.asyncio
async def test_init_with_env_vars():
    """Test initialization with environment variables."""
    # Save original environment variables
    original_backend_url = os.environ.get("FIRECRACKER_BACKEND_URL")
    original_api_key = os.environ.get("FIRECRACKER_API_KEY")
    
    try:
        # Set environment variables for the test
        os.environ["FIRECRACKER_BACKEND_URL"] = "http://env-server.example.com"
        os.environ["FIRECRACKER_API_KEY"] = "env-api-key"
        
        interpreter = FirecrackerInterpreter()
        assert interpreter.backend_url == "http://env-server.example.com"
        assert interpreter.api_key == "env-api-key"
    finally:
        # Restore original environment variables
        if original_backend_url:
            os.environ["FIRECRACKER_BACKEND_URL"] = original_backend_url
        else:
            os.environ.pop("FIRECRACKER_BACKEND_URL", None)
            
        if original_api_key:
            os.environ["FIRECRACKER_API_KEY"] = original_api_key
        else:
            os.environ.pop("FIRECRACKER_API_KEY", None)


@pytest.mark.asyncio
async def test_init_missing_backend_url():
    """Test initialization fails when no backend URL is provided."""
    # Save original environment variable
    original_backend_url = os.environ.get("FIRECRACKER_BACKEND_URL")
    
    try:
        # Remove environment variable if it exists
        os.environ.pop("FIRECRACKER_BACKEND_URL", None)
        
        with pytest.raises(ValueError, match="Missing backend_url"):
            FirecrackerInterpreter()
    finally:
        # Restore original environment variable
        if original_backend_url:
            os.environ["FIRECRACKER_BACKEND_URL"] = original_backend_url


@pytest.mark.asyncio
async def test_initialize(interpreter, mock_client, mock_file_interface):
    """Test initialize method calls spawn_microvm and sets up state correctly."""
    await interpreter.initialize()
    
    # Check that client method was called
    mock_client.return_value.spawn_microvm.assert_called_once()
    
    # Check that interpreter state was updated
    assert interpreter.microvm_id == "test-vm-123"
    assert interpreter._initialized is True
    
    # Check that file interface was created
    mock_file_interface.assert_called_once_with(interpreter.client, "test-vm-123")


@pytest.mark.asyncio
async def test_close(interpreter, mock_client):
    """Test close method cleans up resources correctly."""
    # Set up interpreter state
    interpreter._initialized = True
    interpreter.microvm_id = "test-vm-123"
    
    await interpreter.close()
    
    # Check that client methods were called
    mock_client.return_value.shutdown_microvm.assert_called_once_with("test-vm-123")
    mock_client.return_value.close.assert_called_once()
    
    # Check that interpreter state was updated
    assert interpreter._initialized is False
    assert interpreter.microvm_id is None
    assert interpreter._file_interface is None


@pytest.mark.asyncio
async def test_close_not_initialized(interpreter, mock_client):
    """Test close method handles uninitialized state gracefully."""
    interpreter._initialized = False
    interpreter.microvm_id = None
    
    await interpreter.close()
    
    # Check that microVM shutdown method was not called
    mock_client.return_value.shutdown_microvm.assert_not_called()
    
    # In your implementation, it appears client.close() is not called when not initialized
    # so we verify it wasn't called
    mock_client.return_value.close.assert_not_called()


def test_run_code_not_initialized(interpreter):
    """Test run_code raises error when not initialized."""
    # Set interpreter to uninitialized state
    interpreter._initialized = False
    interpreter.microvm_id = None
    
    # No need to use _run_async at all since we'll raise an error before that
    # This avoids creating any coroutines that might cause warnings
    
    with pytest.raises(RuntimeError, match="not initialized"):
        interpreter.run_code("print('hello')")


def test_run_code(interpreter):
    """Test run_code executes code correctly and returns expected result."""
    # Set up interpreter state
    interpreter._initialized = True
    interpreter.microvm_id = "test-vm-123"
    
    # Mock the _run_async method
    mock_response = {"result": {"stdout": "hello world", "stderr": ""}}
    interpreter._run_async = MagicMock(return_value=mock_response)
    
    # Call method and check results
    result = interpreter.run_code("print('hello world')")
    assert isinstance(result, ExecutionResult)
    assert result.logs == "hello world"
    assert result.error is None
    
    # Check that _run_async was called
    interpreter._run_async.assert_called_once()


def test_run_code_with_error(interpreter):
    """Test run_code properly handles errors."""
    # Set up interpreter state
    interpreter._initialized = True
    interpreter.microvm_id = "test-vm-123"
    
    # Mock the _run_async method with an error response
    mock_response = {"result": {"stdout": "", "stderr": "SyntaxError: invalid syntax"}}
    interpreter._run_async = MagicMock(return_value=mock_response)
    
    # Call method and check results
    result = interpreter.run_code("print('hello world'")  # Missing closing parenthesis
    assert isinstance(result, ExecutionResult)
    assert result.logs == ""
    assert result.error == "SyntaxError: invalid syntax"


def test_run_command_not_initialized(interpreter):
    """Test run_command raises error when not initialized."""
    # Set interpreter to uninitialized state
    interpreter._initialized = False
    interpreter.microvm_id = None
    
    # No need to use _run_async at all since we'll raise an error before that
    # This avoids creating any coroutines that might cause warnings
    
    with pytest.raises(RuntimeError, match="not initialized"):
        interpreter.run_command("ls -la")


def test_run_command(interpreter):
    """Test run_command executes command correctly and returns expected result."""
    # Set up interpreter state
    interpreter._initialized = True
    interpreter.microvm_id = "test-vm-123"
    
    # Mock the _run_async method
    mock_response = {"result": {"stdout": "file1.txt\nfile2.txt", "stderr": ""}}
    interpreter._run_async = MagicMock(return_value=mock_response)
    
    # Call method and check results
    result = interpreter.run_command("ls")
    assert isinstance(result, ExecutionResult)
    assert result.logs == "file1.txt\nfile2.txt"
    assert result.error is None
    
    # Check that _run_async was called
    interpreter._run_async.assert_called_once()


def test_run_command_with_error(interpreter):
    """Test run_command properly handles errors."""
    # Set up interpreter state
    interpreter._initialized = True
    interpreter.microvm_id = "test-vm-123"
    
    # Mock the _run_async method with an error response
    mock_response = {"result": {"stdout": "", "stderr": "command not found: invalid_cmd"}}
    interpreter._run_async = MagicMock(return_value=mock_response)
    
    # Call method and check results
    result = interpreter.run_command("invalid_cmd")
    assert isinstance(result, ExecutionResult)
    assert result.logs == ""
    assert result.error == "command not found: invalid_cmd"


@pytest.mark.asyncio
async def test_run_code_async(interpreter, mock_client):
    """Test _run_code_async method makes correct API calls."""
    # Create payload
    payload = {
        "microvm_id": "test-vm-123",
        "code": "print('hello world')"
    }
    
    # Call method
    result = await interpreter._run_code_async(payload)
    
    # Check result
    assert result == {"result": {"stdout": "code output", "stderr": ""}}
    
    # Check that client method was called with correct arguments
    mock_client.return_value.run_code.assert_called_once_with(payload)


@pytest.mark.asyncio
async def test_run_command_async(interpreter, mock_client):
    """Test _run_command_async method makes correct API calls."""
    # Create payload
    payload = {
        "microvm_id": "test-vm-123",
        "command": "ls -la"
    }
    
    # Call method
    result = await interpreter._run_command_async(payload)
    
    # Check result
    assert result == {"result": {"stdout": "command output", "stderr": ""}}
    
    # Check that client method was called with correct arguments
    mock_client.return_value.run_command.assert_called_once_with(payload)


def test_files_not_initialized(interpreter):
    """Test files property raises error when not initialized."""
    interpreter._initialized = False
    
    with pytest.raises(RuntimeError, match="not initialized"):
        _ = interpreter.files


def test_files(interpreter):
    """Test files property returns the file interface."""
    # Set up interpreter state
    interpreter._initialized = True
    interpreter.microvm_id = "test-vm-123"
    interpreter._file_interface = MagicMock()
    
    file_interface = interpreter.files
    assert file_interface == interpreter._file_interface


def test_create_factory_method(mock_client):
    """Test create class method creates a new instance."""
    with patch('src.sandbox.firecracker.firecracker_interpreter.FirecrackerInterpreter', wraps=FirecrackerInterpreter) as mock_interpreter:
        interpreter = FirecrackerInterpreter.create(
            backend_url="http://test-server.example.com",
            api_key="test-api-key"
        )
        
        # Check that the interpreter was created with correct arguments
        assert isinstance(interpreter, FirecrackerInterpreter)
        assert interpreter.backend_url == "http://test-server.example.com"
        assert interpreter.api_key == "test-api-key"