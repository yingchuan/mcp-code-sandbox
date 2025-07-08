# src/sandbox/docker/docker_file_interface.py
"""
Docker implementation of the file interface.
Provides file operations within Docker containers.
"""
import os
import json
import subprocess
from typing import Dict, Any, List
from pathlib import Path

from src.sandbox.file_interface import FileInterface


class DockerFileInterface(FileInterface):
    """Docker implementation of the file interface"""
    
    def __init__(self, container_name: str):
        """Initialize with container name"""
        self.container_name = container_name
        self.workspace_path = "/home/sandbox/workspace"
    
    def list(self, path: str) -> List[Dict[str, Any]]:
        """List files in the path"""
        # Normalize path to be within workspace
        normalized_path = self._normalize_path(path)
        
        try:
            # Use ls -la with JSON-like output
            result = subprocess.run([
                "docker", "exec", self.container_name, "bash", "-c",
                f"cd {normalized_path} && ls -la --time-style=+%Y-%m-%d_%H:%M:%S | tail -n +2"
            ], capture_output=True, text=True, check=True)
            
            files = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 8:
                        files.append({
                            "name": parts[-1],
                            "type": "directory" if parts[0].startswith('d') else "file",
                            "size": int(parts[4]) if not parts[0].startswith('d') else 0,
                            "permissions": parts[0],
                            "modified": parts[5] + " " + parts[6]
                        })
            
            return files
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to list files in {path}: {e.stderr}")
    
    def read(self, file_path: str) -> str:
        """Read file content"""
        normalized_path = self._normalize_path(file_path)
        
        try:
            result = subprocess.run([
                "docker", "exec", self.container_name, "cat", normalized_path
            ], capture_output=True, text=True, check=True)
            
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to read file {file_path}: {e.stderr}")
    
    def write(self, file_path: str, content: str) -> None:
        """Write content to a file"""
        normalized_path = self._normalize_path(file_path)
        
        try:
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(normalized_path)
            if dir_path != normalized_path:  # Not root
                subprocess.run([
                    "docker", "exec", self.container_name, "mkdir", "-p", dir_path
                ], check=True)
            
            # Write content using bash redirection
            subprocess.run([
                "docker", "exec", self.container_name, "bash", "-c",
                f"cat > {normalized_path}"
            ], input=content, text=True, check=True)
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to write file {file_path}: {e.stderr}")
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path to be within workspace and secure"""
        # Remove leading slash and resolve relative paths
        path = path.lstrip('/')
        
        # Prevent directory traversal
        normalized = os.path.normpath(path)
        if normalized.startswith('..'):
            raise ValueError(f"Path traversal not allowed: {path}")
        
        # Ensure it's within workspace
        return os.path.join(self.workspace_path, normalized)