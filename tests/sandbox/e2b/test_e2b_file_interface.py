# tests/sandbox/e2b/test_e2b_file_interface.py
"""
Tests for the E2BFileInterface class.
These tests use pytest fixtures and mocks to test the file interface without making actual API calls.
"""
import pytest
from unittest.mock import MagicMock, patch

# imports
from src.sandbox.e2b.e2b_file_interface import E2BFileInterface

# Filter out coroutine warnings for the entire module
pytestmark = [
    pytest.mark.filterwarnings("ignore::RuntimeWarning")
]


@pytest.fixture
def mock_sandbox():
    """Fixture to create a mock sandbox for the file interface."""
    sandbox = MagicMock()
    
    # Mock the files attribute
    files = MagicMock()
    files.list = MagicMock()
    files.read = MagicMock()
    files.write = MagicMock()
    
    # Set up the files attribute on the sandbox
    sandbox.files = files
    
    return sandbox


@pytest.fixture
def file_interface(mock_sandbox):
    """Fixture to create an E2BFileInterface instance with a mock sandbox."""
    return E2BFileInterface(mock_sandbox)


def test_init(mock_sandbox):
    """Test initialization of E2BFileInterface."""
    file_interface = E2BFileInterface(mock_sandbox)
    assert file_interface._sandbox == mock_sandbox


def test_list(file_interface, mock_sandbox):
    """Test list method makes correct calls and returns expected results."""
    # Setup mock response
    mock_files = [
        {"name": "file1.txt", "type": "file", "size": 100},
        {"name": "file2.txt", "type": "file", "size": 200},
        {"name": "dir1", "type": "directory", "size": 4096}
    ]
    mock_sandbox.files.list.return_value = mock_files
    
    # Call method
    result = file_interface.list("/path/to/dir")
    
    # Check result
    assert result == mock_files
    
    # Check that sandbox method was called with correct arguments
    mock_sandbox.files.list.assert_called_once_with("/path/to/dir")


def test_read(file_interface, mock_sandbox):
    """Test read method makes correct calls and returns expected results."""
    # Setup mock response
    file_content = "line 1\nline 2\nline 3"
    mock_sandbox.files.read.return_value = file_content
    
    # Call method
    result = file_interface.read("/path/to/file.txt")
    
    # Check result
    assert result == file_content
    
    # Check that sandbox method was called with correct arguments
    mock_sandbox.files.read.assert_called_once_with("/path/to/file.txt")


def test_write(file_interface, mock_sandbox):
    """Test write method makes correct calls."""
    # Define test data
    file_path = "/path/to/file.txt"
    content = "line 1\nline 2\nline 3"
    
    # Call method
    file_interface.write(file_path, content)
    
    # Check that sandbox method was called with correct arguments
    mock_sandbox.files.write.assert_called_once_with(file_path, content)


def test_list_error_handling(file_interface, mock_sandbox):
    """Test list method handles errors properly."""
    # Setup mock to raise an exception
    mock_sandbox.files.list.side_effect = Exception("Failed to list files")
    
    # Call method and verify exception is propagated
    with pytest.raises(Exception, match="Failed to list files"):
        file_interface.list("/path/to/dir")


def test_read_error_handling(file_interface, mock_sandbox):
    """Test read method handles errors properly."""
    # Setup mock to raise an exception
    mock_sandbox.files.read.side_effect = Exception("Failed to read file")
    
    # Call method and verify exception is propagated
    with pytest.raises(Exception, match="Failed to read file"):
        file_interface.read("/path/to/file.txt")


def test_write_error_handling(file_interface, mock_sandbox):
    """Test write method handles errors properly."""
    # Setup mock to raise an exception
    mock_sandbox.files.write.side_effect = Exception("Failed to write file")
    
    # Call method and verify exception is propagated
    with pytest.raises(Exception, match="Failed to write file"):
        file_interface.write("/path/to/file.txt", "content")


def test_interface_methods_match_sandbox(mock_sandbox):
    """
    Test to ensure that the E2BFileInterface methods correctly map to the underlying
    sandbox methods without any transformation or additional logic.
    """
    # Create a file interface
    file_interface = E2BFileInterface(mock_sandbox)
    
    # Set up unique return values for sandbox methods
    mock_sandbox.files.list.return_value = "list_result"
    mock_sandbox.files.read.return_value = "read_result"
    
    # Test that the interface methods directly return what the sandbox methods return
    assert file_interface.list("/test") == "list_result"
    assert file_interface.read("/test.txt") == "read_result"
    
    # Also verify that write is passed through directly
    file_interface.write("/test.txt", "content")
    mock_sandbox.files.write.assert_called_once_with("/test.txt", "content")