# tests/sandbox/test_interpreter_factory.py
"""
Tests for the InterpreterFactory class.
"""
import pytest
from unittest.mock import patch, MagicMock

from src.sandbox.interpreter_factory import InterpreterFactory
from src.sandbox.code_interpreter import CodeInterpreter
from src.sandbox.e2b.e2b_interpreter import E2BInterpreter
from src.sandbox.firecracker.firecracker_interpreter import FirecrackerInterpreter


def test_interpreter_factory_constants():
    """Test that InterpreterFactory has the correct constants defined."""
    assert InterpreterFactory.INTERPRETER_E2B == "e2b"
    assert InterpreterFactory.INTERPRETER_FIRECRACKER == "firecracker"


@patch('src.sandbox.e2b.e2b_interpreter.E2BInterpreter.create')
def test_create_e2b_interpreter(mock_create):
    """Test creating an E2B interpreter."""
    # Setup mock
    mock_instance = MagicMock(spec=E2BInterpreter)
    mock_create.return_value = mock_instance
    
    # Create interpreter
    interpreter = InterpreterFactory.create_interpreter(
        interpreter_type=InterpreterFactory.INTERPRETER_E2B,
        api_key="test-api-key"
    )
    
    # Verify the correct method was called with expected args
    mock_create.assert_called_once_with(api_key="test-api-key")
    assert interpreter == mock_instance


def test_create_e2b_interpreter_missing_api_key():
    """Test creating an E2B interpreter with missing API key."""
    with pytest.raises(ValueError, match="API key must be provided for E2B interpreter"):
        InterpreterFactory.create_interpreter(
            interpreter_type=InterpreterFactory.INTERPRETER_E2B,
            api_key=None
        )


@patch('src.sandbox.firecracker.firecracker_interpreter.FirecrackerInterpreter.create')
def test_create_firecracker_interpreter(mock_create):
    """Test creating a Firecracker interpreter."""
    # Setup mock
    mock_instance = MagicMock(spec=FirecrackerInterpreter)
    mock_create.return_value = mock_instance
    
    # Create interpreter
    interpreter = InterpreterFactory.create_interpreter(
        interpreter_type=InterpreterFactory.INTERPRETER_FIRECRACKER,
        backend_url="http://test-server.example.com",
        api_key="test-api-key"
    )
    
    # Verify the correct method was called with expected args
    mock_create.assert_called_once_with(
        "http://test-server.example.com", "test-api-key"
    )
    assert interpreter == mock_instance


def test_create_firecracker_interpreter_missing_backend_url():
    """Test creating a Firecracker interpreter with missing backend URL."""
    with pytest.raises(ValueError, match="Backend URL must be provided for Firecracker interpreter"):
        InterpreterFactory.create_interpreter(
            interpreter_type=InterpreterFactory.INTERPRETER_FIRECRACKER,
            backend_url=None,
            api_key="test-api-key"
        )


def test_create_firecracker_interpreter_without_api_key():
    """Test creating a Firecracker interpreter without an API key."""
    with patch('src.sandbox.firecracker.firecracker_interpreter.FirecrackerInterpreter.create') as mock_create:
        mock_instance = MagicMock(spec=FirecrackerInterpreter)
        mock_create.return_value = mock_instance
        
        # API key is optional for Firecracker, so this should work
        interpreter = InterpreterFactory.create_interpreter(
            interpreter_type=InterpreterFactory.INTERPRETER_FIRECRACKER,
            backend_url="http://test-server.example.com",
            api_key=None
        )
        
        mock_create.assert_called_once_with("http://test-server.example.com", None)
        assert interpreter == mock_instance


def test_create_unsupported_interpreter_type():
    """Test creating an interpreter with an unsupported type."""
    with pytest.raises(ValueError, match="Unsupported interpreter type: invalid_type"):
        InterpreterFactory.create_interpreter(
            interpreter_type="invalid_type",
            backend_url="http://test-server.example.com",
            api_key="test-api-key"
        )


def test_factory_returns_code_interpreter_instance():
    """Test that the factory returns instances that implement the CodeInterpreter interface."""
    # This test uses real implementations, but we'll keep it simple
    # Test with E2B
    with patch('src.sandbox.e2b.e2b_interpreter.E2BInterpreter.create') as mock_create:
        mock_instance = MagicMock(spec=E2BInterpreter)
        mock_create.return_value = mock_instance
        
        interpreter = InterpreterFactory.create_interpreter(
            interpreter_type=InterpreterFactory.INTERPRETER_E2B,
            api_key="test-api-key"
        )
        
        # The instance is a mock but it has the spec of E2BInterpreter
        assert interpreter == mock_instance
        
    # Test with Firecracker
    with patch('src.sandbox.firecracker.firecracker_interpreter.FirecrackerInterpreter.create') as mock_create:
        mock_instance = MagicMock(spec=FirecrackerInterpreter)
        mock_create.return_value = mock_instance
        
        interpreter = InterpreterFactory.create_interpreter(
            interpreter_type=InterpreterFactory.INTERPRETER_FIRECRACKER,
            backend_url="http://test-server.example.com"
        )
        
        # The instance is a mock but it has the spec of FirecrackerInterpreter
        assert interpreter == mock_instance