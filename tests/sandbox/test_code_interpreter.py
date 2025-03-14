# tests/sandbox/test_code_interpreter.py
"""
Tests for the CodeInterpreter abstract base class and ExecutionResult class.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import inspect

from src.sandbox.code_interpreter import CodeInterpreter, ExecutionResult
from src.sandbox.file_interface import FileInterface


def test_execution_result_init():
    """Test initialization of ExecutionResult class."""
    # Test with default values
    result = ExecutionResult()
    assert result.logs == ""
    assert result.error is None
    
    # Test with specific values
    result = ExecutionResult(logs="some logs", error="some error")
    assert result.logs == "some logs"
    assert result.error == "some error"


def test_code_interpreter_abstract_methods():
    """Test that CodeInterpreter properly defines abstract methods."""
    # Get the list of abstract methods
    abstract_methods = CodeInterpreter.__abstractmethods__
    
    # Check that all required methods are abstract
    assert 'initialize' in abstract_methods
    assert 'close' in abstract_methods
    assert 'run_code' in abstract_methods
    assert 'run_command' in abstract_methods
    assert 'files' in abstract_methods
    assert 'create' in abstract_methods
    
    # Check method signatures
    initialize_sig = inspect.signature(CodeInterpreter.initialize)
    assert initialize_sig.return_annotation == None
    
    close_sig = inspect.signature(CodeInterpreter.close)
    assert close_sig.return_annotation == None
    
    run_code_sig = inspect.signature(CodeInterpreter.run_code)
    assert 'code' in run_code_sig.parameters
    assert run_code_sig.return_annotation == ExecutionResult
    
    run_command_sig = inspect.signature(CodeInterpreter.run_command)
    assert 'command' in run_command_sig.parameters
    assert run_command_sig.return_annotation == ExecutionResult
    
    files_property = CodeInterpreter.files
    assert files_property.fget.__annotations__['return'] == FileInterface


# Create a minimal concrete implementation for testing
class MockInterpreter(CodeInterpreter):
    """Mock implementation of CodeInterpreter for testing."""
    
    async def initialize(self) -> None:
        pass
    
    async def close(self) -> None:
        pass
    
    def run_code(self, code: str) -> ExecutionResult:
        return ExecutionResult(logs=f"Executed code: {code}")
    
    def run_command(self, command: str) -> ExecutionResult:
        return ExecutionResult(logs=f"Executed command: {command}")
    
    @property
    def files(self) -> FileInterface:
        return MagicMock(spec=FileInterface)
    
    @classmethod
    def create(cls, *args, **kwargs) -> 'CodeInterpreter':
        return cls()


def test_mock_interpreter_conforms_to_interface():
    """Test that our mock implementation conforms to the CodeInterpreter interface."""
    interpreter = MockInterpreter()
    
    # Check that the interpreter can be instantiated
    assert isinstance(interpreter, CodeInterpreter)
    
    # Check that all interface methods are implemented
    assert hasattr(interpreter, 'initialize')
    assert hasattr(interpreter, 'close')
    assert hasattr(interpreter, 'run_code')
    assert hasattr(interpreter, 'run_command')
    assert hasattr(interpreter, 'files')
    assert hasattr(interpreter.__class__, 'create')


@pytest.mark.asyncio
async def test_mock_interpreter_methods():
    """Test the behavior of the mock interpreter's methods."""
    interpreter = MockInterpreter()
    
    # Test initialize and close (should not raise exceptions)
    await interpreter.initialize()
    await interpreter.close()
    
    # Test run_code
    result = interpreter.run_code("print('hello')")
    assert isinstance(result, ExecutionResult)
    assert "Executed code: print('hello')" in result.logs
    
    # Test run_command
    result = interpreter.run_command("ls -la")
    assert isinstance(result, ExecutionResult)
    assert "Executed command: ls -la" in result.logs
    
    # Test files property
    files = interpreter.files
    assert files is not None


def test_create_factory_method():
    """Test the create factory method."""
    interpreter = MockInterpreter.create()
    assert isinstance(interpreter, MockInterpreter)
    assert isinstance(interpreter, CodeInterpreter)