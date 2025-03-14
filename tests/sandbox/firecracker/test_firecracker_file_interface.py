# tests/sandbox/firecracker/test_firecracker_file_interface.py
"""
Tests for the FirecrackerFileInterface class.
These tests use pytest fixtures and mocks to test the file interface without making actual HTTP requests.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

from src.sandbox.firecracker.firecracker_file_interface import FirecrackerFileInterface

# Filter out coroutine warnings for the entire module
pytestmark = [
    pytest.mark.filterwarnings("ignore::RuntimeWarning")
]


@pytest.fixture
def mock_client():
    """Fixture to create a mock client for the file interface."""
    client = MagicMock()
    client.run_command = AsyncMock()
    client.run_code = AsyncMock()
    return client


@pytest.fixture
def file_interface(mock_client):
    """Fixture to create a FirecrackerFileInterface instance with a mock client."""
    return FirecrackerFileInterface(mock_client, "test-vm-123")


# Instead of mocking _run_async which creates the coroutines,
# we'll patch the individual methods to avoid creating coroutines
@pytest.fixture
def patched_file_interface(file_interface):
    """File interface with patched methods to prevent coroutine warnings."""
    # Create simple mock results
    with patch.object(file_interface, '_run_async') as mock_run_async:
        def mock_side_effect(coro):
            # We don't evaluate the coroutine at all, just return test data
            if '_list_files' in str(coro):
                return "total 20\ndrwxr-xr-x 4 user group 4096 Mar 10 10:00 .\ndrwxr-xr-x 4 user group 4096 Mar 10 09:00 ..\n-rw-r--r-- 1 user group 100 Mar 10 10:00 file1.txt\n-rw-r--r-- 1 user group 200 Mar 10 10:01 file2.txt"
            if '_read_file' in str(coro):
                return "line 1\nline 2\nline 3"
            return None
        
        mock_run_async.side_effect = mock_side_effect
        yield file_interface


def test_init(mock_client):
    """Test initialization of FirecrackerFileInterface."""
    file_interface = FirecrackerFileInterface(mock_client, "test-vm-123")
    assert file_interface.client == mock_client
    assert file_interface.microvm_id == "test-vm-123"


def test_list(patched_file_interface):
    """Test list method makes correct calls and returns expected results."""
    # Call method
    result = patched_file_interface.list("/path/to/dir")
    
    # Check result
    assert len(result) == 4  # 4 entries including . and ..
    assert result[2]["name"] == "file1.txt"
    assert result[2]["type"] == "file"
    assert result[2]["size"] == 100
    assert result[3]["name"] == "file2.txt"
    assert result[3]["size"] == 200


def test_read(patched_file_interface):
    """Test read method makes correct calls and returns expected results."""
    # Call method
    result = patched_file_interface.read("/path/to/file.txt")
    
    # Check result
    assert result == "line 1\nline 2\nline 3"


def test_write(patched_file_interface):
    """Test write method makes correct calls."""
    # Call method
    patched_file_interface.write("/path/to/file.txt", "line 1\nline 2\nline 3")
    # We can't check much here since we've patched the method to do nothing


@pytest.mark.asyncio
async def test_list_files_async(file_interface, mock_client):
    """Test _list_files method makes correct API calls."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = "file1.txt\nfile2.txt"
    mock_client.run_command.return_value = mock_response
    
    # Create payload
    payload = {
        "microvm_id": "test-vm-123",
        "action": "run_command",
        "command": "ls -la /path/to/dir"
    }
    
    # Call method
    result = await file_interface._list_files("/path/to/dir", payload)
    
    # Check result
    assert result == "file1.txt\nfile2.txt"
    
    # Check that client method was called with correct arguments
    mock_client.run_command.assert_called_once_with(payload)


@pytest.mark.asyncio
async def test_read_file_async(file_interface, mock_client):
    """Test _read_file method makes correct API calls."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = "file content"
    mock_client.run_command.return_value = mock_response
    
    # Create payload
    payload = {
        "microvm_id": "test-vm-123",
        "action": "run_command",
        "command": "cat /path/to/file.txt"
    }
    
    # Call method
    result = await file_interface._read_file("/path/to/file.txt", payload)
    
    # Check result
    assert result == "file content"
    
    # Check that client method was called with correct arguments
    mock_client.run_command.assert_called_once_with(payload)


@pytest.mark.asyncio
async def test_write_file_async(file_interface, mock_client):
    """Test _write_file method makes correct API calls."""
    # Create payload
    payload = {
        "microvm_id": "test-vm-123",
        "action": "run_code",
        "code": 'with open("/path/to/file.txt", "w") as f:\n    f.write("file content")'
    }
    
    # Call method
    await file_interface._write_file("/path/to/file.txt", "file content", payload)
    
    # Check that client method was called with correct arguments
    mock_client.run_code.assert_called_once_with(payload)


def test_parse_ls_output(file_interface):
    """Test _parse_ls_output correctly parses ls command output."""
    ls_output = """total 20
drwxr-xr-x 4 user group 4096 Mar 10 10:00 .
drwxr-xr-x 4 user group 4096 Mar 10 09:00 ..
-rw-r--r-- 1 user group 100 Mar 10 10:00 file1.txt
-rw-r--r-- 1 user group 200 Mar 10 10:01 file2.txt
drwxr-xr-x 2 user group 4096 Mar 10 10:02 dir1
-rw-r--r-- 1 user group 300 Mar 10 10:03 file with spaces.txt
"""
    
    result = file_interface._parse_ls_output(ls_output)
    
    # Check number of entries
    assert len(result) == 6  # 6 entries including . and ..
    
    # Check file entries
    assert result[2]["name"] == "file1.txt"
    assert result[2]["type"] == "file"
    assert result[2]["size"] == 100
    assert result[2]["permissions"] == "-rw-r--r--"
    assert result[2]["owner"] == "user"
    assert result[2]["group"] == "group"
    assert result[2]["modified"] == "Mar 10 10:00"
    
    # Check directory entry
    assert result[4]["name"] == "dir1"
    assert result[4]["type"] == "directory"
    
    # Check file with spaces
    assert result[5]["name"] == "file with spaces.txt"
    assert result[5]["size"] == 300