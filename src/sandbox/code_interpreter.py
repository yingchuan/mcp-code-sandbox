# src/sandbox/code_interpreter.py
"""
Abstract base class for code interpreter implementations.
This provides a common interface for different code execution backends.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

# imports
from sandbox.file_interface import FileInterface


class ExecutionResult:
    """Class representing the result of code execution"""
    
    def __init__(self, logs: str = "", error: Optional[str] = None):
        self.logs = logs
        self.error = error

class CodeInterpreter(ABC):
    """Abstract base class for code interpreters"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the interpreter"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Clean up resources"""
        pass
    
    @abstractmethod
    def run_code(self, code: str) -> ExecutionResult:
        """Execute code and return the result"""
        pass
    
    @abstractmethod
    def run_command(self, command: str) -> ExecutionResult:
        """Run a shell command and return the result"""
        pass
    
    @property
    @abstractmethod
    def files(self) -> FileInterface:
        """Get the file interface"""
        pass
    
    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> 'CodeInterpreter':
        """Factory method to create an interpreter instance"""
        pass