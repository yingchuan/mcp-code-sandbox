# src/sandbox/file_interface.py
"""
Abstract base class for code interpreter implementations.
This provides a common interface for different code execution backends.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class FileInterface(ABC):
    """Abstract interface for file operations"""
    
    @abstractmethod
    def list(self, path: str) -> List[Dict[str, Any]]:
        """List files in the path"""
        pass
    
    @abstractmethod
    def read(self, file_path: str) -> str:
        """Read file content"""
        pass
    
    @abstractmethod
    def write(self, file_path: str, content: str) -> None:
        """Write content to a file"""
        pass