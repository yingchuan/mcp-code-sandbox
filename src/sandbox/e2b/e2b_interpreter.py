# src/sandbox/e2b/e2b_interpreter.py
"""
E2B implementation of the code interpreter interface.
Wraps the e2b_code_interpreter library to conform to our abstract base class.
"""
import os
from typing import Dict, Any, List, Optional

# imports
from e2b_code_interpreter import Sandbox as E2BSandbox
from src.sandbox.code_interpreter import CodeInterpreter, ExecutionResult, FileInterface
from src.sandbox.e2b.e2b_file_interface import E2BFileInterface

class E2BInterpreter(CodeInterpreter):
    """E2B implementation of the code interpreter"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with optional API key"""
        self._api_key = api_key or os.environ.get("E2B_API_KEY")
        self._sandbox = None
        self._file_interface = None
    
    async def initialize(self) -> None:
        """Initialize the E2B sandbox"""
        if not self._sandbox:
            # Pass API key if provided, otherwise E2B will look for it in env vars
            if self._api_key:
                self._sandbox = E2BSandbox(api_key=self._api_key)
            else:
                self._sandbox = E2BSandbox()
            self._file_interface = E2BFileInterface(self._sandbox)
    
    async def close(self) -> None:
        """Clean up E2B sandbox resources"""
        if self._sandbox:
            await self._sandbox.close()
            self._sandbox = None
            self._file_interface = None
    
    def run_code(self, code: str) -> ExecutionResult:
        """Execute code and return the result"""
        if not self._sandbox:
            raise RuntimeError("Interpreter not initialized. Call initialize() first.")
        
        execution = self._sandbox.run_code(code)
        return ExecutionResult(
            logs=execution.logs,
            error=execution.error
        )
    
    def run_command(self, command: str) -> ExecutionResult:
        """Run a shell command and return the result"""
        if not self._sandbox:
            raise RuntimeError("Interpreter not initialized. Call initialize() first.")
        
        execution = self._sandbox.run_command(command)
        return ExecutionResult(
            logs=execution.logs,
            error=execution.error
        )
    
    @property
    def files(self) -> FileInterface:
        """Get the file interface"""
        if not self._sandbox or not self._file_interface:
            raise RuntimeError("Interpreter not initialized. Call initialize() first.")
        
        return self._file_interface
    
    @classmethod
    def create(cls, api_key: Optional[str] = None) -> 'E2BInterpreter':
        """Factory method to create an interpreter instance"""
        return cls(api_key)