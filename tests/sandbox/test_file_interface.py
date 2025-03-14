# tests/sandbox/test_file_interface.py
"""
Tests for the FileInterface abstract base class.
"""
import pytest
import inspect
from unittest.mock import MagicMock

from src.sandbox.file_interface import FileInterface


def test_file_interface_abstract_methods():
    """Test that FileInterface properly defines abstract methods."""
    # Get the list of abstract methods
    abstract_methods = FileInterface.__abstractmethods__
    
    # Check that all required methods are abstract
    assert 'list' in abstract_methods
    assert 'read' in abstract_methods
    assert 'write' in abstract_methods
    
    # Check method signatures
    list_sig = inspect.signature(FileInterface.list)
    assert 'path' in list_sig.parameters
    assert list_sig.return_annotation.__origin__ == list
    
    read_sig = inspect.signature(FileInterface.read)
    assert 'file_path' in read_sig.parameters
    assert read_sig.return_annotation == str
    
    write_sig = inspect.signature(FileInterface.write)
    assert 'file_path' in write_sig.parameters
    assert 'content' in write_sig.parameters
    assert write_sig.return_annotation == None


# Create a minimal concrete implementation for testing
class MockFileInterface(FileInterface):
    """Mock implementation of FileInterface for testing."""
    
    def list(self, path):
        return [
            {"name": "file1.txt", "type": "file", "size": 100},
            {"name": "dir1", "type": "directory", "size": 0}
        ]
    
    def read(self, file_path):
        return f"Content of {file_path}"
    
    def write(self, file_path, content):
        pass  # Do nothing, this is just a mock


def test_mock_file_interface_conforms_to_interface():
    """Test that our mock implementation conforms to the FileInterface interface."""
    file_interface = MockFileInterface()
    
    # Check that the file interface can be instantiated
    assert isinstance(file_interface, FileInterface)
    
    # Check that all interface methods are implemented
    assert hasattr(file_interface, 'list')
    assert hasattr(file_interface, 'read')
    assert hasattr(file_interface, 'write')


def test_mock_file_interface_methods():
    """Test the behavior of the mock file interface's methods."""
    file_interface = MockFileInterface()
    
    # Test list
    result = file_interface.list("/path/to/dir")
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "file1.txt"
    assert result[1]["type"] == "directory"
    
    # Test read
    content = file_interface.read("/path/to/file.txt")
    assert isinstance(content, str)
    assert content == "Content of /path/to/file.txt"
    
    # Test write (should not raise exceptions)
    file_interface.write("/path/to/file.txt", "new content")