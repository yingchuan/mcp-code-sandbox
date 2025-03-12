# src/sandbox/e2b/e2b_file_interface.py
"""
E2B implementation of the code interpreter interface.
Wraps the e2b_code_interpreter library to conform to our abstract base class.
"""
import os
from typing import Dict, Any, List

# imports
from sandbox.code_interpreter import FileInterface


class E2BFileInterface(FileInterface):
    """E2B implementation of file operations"""
    
    def __init__(self, sandbox):
        self._sandbox = sandbox
    
    def list(self, path: str) -> List[Dict[str, Any]]:
        """List files in the path"""
        return self._sandbox.files.list(path)
    
    def read(self, file_path: str) -> str:
        """Read file content"""
        return self._sandbox.files.read(file_path)
    
    def write(self, file_path: str, content: str) -> None:
        """Write content to a file"""
        self._sandbox.files.write(file_path, content)
