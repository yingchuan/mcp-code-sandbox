# tests/sandbox/e2b/test_e2b_interpreter.py
"""
Tests for the E2BInterpreter class.
These tests use pytest fixtures and mocks to test the interpreter without a real E2B sandbox.
"""
import pytest
import os
from unittest.mock import MagicMock, patch, AsyncMock

from src.sandbox.e2b.e2b_interpreter import E2BInterpreter
from src.sandbox.code_interpreter import ExecutionResult
from src.sandbox.e2b.e2b_file_interface import E2BFileInterface

# Filter out any coroutine warnings
pytestmark = [
    pytest.mark.filterwarnings("ignore::RuntimeWarning")
]


@pytest.fixture
def mock_e2b_sandbox():
    """Fixture to create a mock E2B sandbox."""
    # We don't directly patch e2b_code_interpreter.Sandbox here because
    # we need to patch the import in the implementation
    mock_sandbox = MagicMock()
    mock_sandbox.run_code = MagicMock()
    mock_sandbox.run_command = MagicMock()
    mock_sandbox.close = AsyncMock()
    
    yield mock_sandbox


@pytest.fixture
def mock_file_interface():
    """Fixture to create a mock E2BFileInterface."""
    with patch('src.sandbox.e2b.e2b_interpreter.E2BFileInterface') as mock_file_interface_class:
        mock_file_interface = MagicMock()
        mock_file_interface_class.return_value = mock_file_interface
        yield mock_file_interface


@pytest.fixture
def interpreter(mock_e2b_sandbox, mock_file_interface):
    """Fixture to create an E2BInterpreter instance with mocked dependencies."""
    return E2BInterpreter(api_key="test-api-key")


@pytest.mark.asyncio
async def test_init_with_direct_api_key():
    """Test initialization with directly provided API key."""
    interpreter = E2BInterpreter(api_key="test-api-key")
    assert interpreter._api_key == "test-api-key"
    assert interpreter._sandbox is None
    assert interpreter._file_interface is None


@pytest.mark.asyncio
async def test_init_with_env_var():
    """Test initialization with API key from environment variable."""
    # Save original environment variable
    original_api_key = os.environ.get("E2B_API_KEY")
    
    try:
        # Set environment variable for the test
        os.environ["E2B_API_KEY"] = "env-api-key"
        
        interpreter = E2BInterpreter()
        assert interpreter._api_key == "env-api-key"
    finally:
        # Restore original environment variable
        if original_api_key:
            os.environ["E2B_API_KEY"] = original_api_key
        else:
            os.environ.pop("E2B_API_KEY", None)


@pytest.mark.asyncio
async def test_initialize_with_api_key(interpreter, mock_e2b_sandbox):
    """Test initialize method creates sandbox with API key."""
    # We need to patch the actual E2BSandbox import in the implementation
    with patch('src.sandbox.e2b.e2b_interpreter.E2BSandbox') as mock_sandbox_class:
        mock_sandbox_class.return_value = mock_e2b_sandbox
        
        await interpreter.initialize()
        
        # Check that sandbox was created with API key
        mock_sandbox_class.assert_called_once_with(api_key="test-api-key")
        assert interpreter._sandbox == mock_e2b_sandbox
        assert interpreter._file_interface is not None


@pytest.mark.asyncio
async def test_initialize_without_api_key():
    """Test initialize method creates sandbox without explicit API key."""
    # We need to patch the actual E2BSandbox import in the implementation
    with patch('src.sandbox.e2b.e2b_interpreter.E2BSandbox') as mock_sandbox_class:
        # Create and configure the mock sandbox instance
        mock_sandbox = MagicMock()
        mock_sandbox_class.return_value = mock_sandbox
        
        # Create interpreter without API key
        interpreter = E2BInterpreter(api_key=None)
        await interpreter.initialize()
        
        # Check that sandbox was created without API key parameters
        mock_sandbox_class.assert_called_once_with()
        assert interpreter._sandbox == mock_sandbox


@pytest.mark.asyncio
async def test_close(interpreter, mock_e2b_sandbox):
    """Test close method cleans up resources correctly."""
    # Set up interpreter state
    interpreter._sandbox = mock_e2b_sandbox
    interpreter._file_interface = MagicMock()
    
    await interpreter.close()
    
    # Check that sandbox was closed
    mock_e2b_sandbox.close.assert_called_once()
    assert interpreter._sandbox is None
    assert interpreter._file_interface is None


@pytest.mark.asyncio
async def test_close_not_initialized(interpreter, mock_e2b_sandbox):
    """Test close method handles uninitialized state gracefully."""
    interpreter._sandbox = None
    interpreter._file_interface = None
    
    # Should not raise an exception
    await interpreter.close()


def test_run_code_not_initialized(interpreter):
    """Test run_code raises error when not initialized."""
    interpreter._sandbox = None
    
    with pytest.raises(RuntimeError, match="not initialized"):
        interpreter.run_code("print('hello')")


def test_run_code(interpreter, mock_e2b_sandbox):
    """Test run_code executes code correctly and returns expected result."""
    # Setup mock response
    mock_execution_result = MagicMock()
    mock_execution_result.logs = "hello world"
    mock_execution_result.error = None
    mock_e2b_sandbox.run_code.return_value = mock_execution_result
    
    # Set up interpreter state
    interpreter._sandbox = mock_e2b_sandbox
    
    # Call method and check results
    result = interpreter.run_code("print('hello world')")
    assert isinstance(result, ExecutionResult)
    assert result.logs == "hello world"
    assert result.error is None
    
    # Check that sandbox method was called with correct arguments
    mock_e2b_sandbox.run_code.assert_called_once_with("print('hello world')")


def test_run_code_with_error(interpreter, mock_e2b_sandbox):
    """Test run_code properly handles errors."""
    # Setup mock response
    mock_execution_result = MagicMock()
    mock_execution_result.logs = ""
    mock_execution_result.error = "SyntaxError: invalid syntax"
    mock_e2b_sandbox.run_code.return_value = mock_execution_result
    
    # Set up interpreter state
    interpreter._sandbox = mock_e2b_sandbox
    
    # Call method and check results
    result = interpreter.run_code("print('hello world'")  # Missing closing parenthesis
    assert isinstance(result, ExecutionResult)
    assert result.logs == ""
    assert result.error == "SyntaxError: invalid syntax"


def test_run_command_not_initialized(interpreter):
    """Test run_command raises error when not initialized."""
    interpreter._sandbox = None
    
    with pytest.raises(RuntimeError, match="not initialized"):
        interpreter.run_command("ls -la")


def test_run_command(interpreter, mock_e2b_sandbox):
    """Test run_command executes command correctly and returns expected result."""
    # Setup mock response
    mock_execution_result = MagicMock()
    mock_execution_result.logs = "file1.txt\nfile2.txt"
    mock_execution_result.error = None
    mock_e2b_sandbox.run_command.return_value = mock_execution_result
    
    # Set up interpreter state
    interpreter._sandbox = mock_e2b_sandbox
    
    # Call method and check results
    result = interpreter.run_command("ls")
    assert isinstance(result, ExecutionResult)
    assert result.logs == "file1.txt\nfile2.txt"
    assert result.error is None
    
    # Check that sandbox method was called with correct arguments
    mock_e2b_sandbox.run_command.assert_called_once_with("ls")


def test_run_command_with_error(interpreter, mock_e2b_sandbox):
    """Test run_command properly handles errors."""
    # Setup mock response
    mock_execution_result = MagicMock()
    mock_execution_result.logs = ""
    mock_execution_result.error = "command not found: invalid_cmd"
    mock_e2b_sandbox.run_command.return_value = mock_execution_result
    
    # Set up interpreter state
    interpreter._sandbox = mock_e2b_sandbox
    
    # Call method and check results
    result = interpreter.run_command("invalid_cmd")
    assert isinstance(result, ExecutionResult)
    assert result.logs == ""
    assert result.error == "command not found: invalid_cmd"


def test_files_not_initialized(interpreter):
    """Test files property raises error when not initialized."""
    interpreter._sandbox = None
    interpreter._file_interface = None
    
    with pytest.raises(RuntimeError, match="not initialized"):
        _ = interpreter.files


def test_files(interpreter, mock_file_interface):
    """Test files property returns the file interface."""
    # Set up interpreter state
    interpreter._sandbox = MagicMock()
    interpreter._file_interface = mock_file_interface
    
    file_interface = interpreter.files
    assert file_interface == mock_file_interface


def test_create_factory_method():
    """Test create class method creates a new instance."""
    with patch('src.sandbox.e2b.e2b_interpreter.E2BInterpreter', wraps=E2BInterpreter) as mock_interpreter_class:
        interpreter = E2BInterpreter.create(api_key="test-api-key")
        
        # Check that the interpreter was created with correct arguments
        assert isinstance(interpreter, E2BInterpreter)
        assert interpreter._api_key == "test-api-key"