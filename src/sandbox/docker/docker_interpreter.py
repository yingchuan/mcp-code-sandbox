# src/sandbox/docker/docker_interpreter.py
"""
Docker implementation of the code interpreter interface.
Uses Docker containers for secure code execution with uv for Python package management.
"""
import os
import subprocess
import uuid
import tempfile
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.sandbox.code_interpreter import CodeInterpreter, ExecutionResult
from src.sandbox.docker.docker_file_interface import DockerFileInterface


class DockerInterpreter(CodeInterpreter):
    """Docker implementation of the code interpreter"""
    
    def __init__(self, image_name: str = "yingchuan/devenv:latest", 
                 container_name: Optional[str] = None,
                 workspace_mount: Optional[str] = None):
        """Initialize with Docker image and container settings"""
        self.image_name = image_name
        self.container_name = container_name or f"mcp-sandbox-{uuid.uuid4().hex[:8]}"
        self.workspace_mount = workspace_mount or str(Path.home() / "tmp" / "mcp-sandbox")
        self._file_interface = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the Docker container"""
        if self._initialized:
            return
            
        try:
            # Ensure workspace directory exists
            os.makedirs(self.workspace_mount, exist_ok=True)
            
            # Check if image exists
            result = subprocess.run([
                "docker", "image", "inspect", self.image_name
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Docker image {self.image_name} not found. Please build it first.")
            
            # Stop and remove existing container if it exists
            subprocess.run([
                "docker", "stop", self.container_name
            ], capture_output=True, text=True)
            
            subprocess.run([
                "docker", "rm", self.container_name
            ], capture_output=True, text=True)
            
            # Start the container in detached mode
            cmd = [
                "docker", "run", "-d",
                "--name", self.container_name,
                "--hostname", "mcp-sandbox",
                "-v", f"{self.workspace_mount}:/home/sandbox/workspace",
                "--network", "none",  # No network access for security
                "--workdir", "/home/sandbox/workspace",
                self.image_name,
                "tail", "-f", "/dev/null"  # Keep container running
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Create sandbox workspace and ensure permissions
            subprocess.run([
                "docker", "exec", self.container_name, "bash", "-c",
                """
                # Create workspace directory
                mkdir -p /home/sandbox/workspace
                
                # Set permissions for current user
                current_user=$(whoami)
                if [ "$current_user" != "root" ]; then
                    # If not root, just ensure the workspace exists
                    cd /home/sandbox/workspace
                else
                    # If root, create a sandbox user
                    if ! id sandbox >/dev/null 2>&1; then
                        useradd -m -s /bin/bash sandbox
                    fi
                    chown -R sandbox:sandbox /home/sandbox
                fi
                """
            ], check=True)
            
            # Initialize uv and create virtual environment
            subprocess.run([
                "docker", "exec", self.container_name, "bash", "-c",
                """
                # Source Nix environment
                if [ -f ~/.nix-profile/etc/profile.d/nix.sh ]; then
                    source ~/.nix-profile/etc/profile.d/nix.sh
                fi
                
                # Create a basic pyproject.toml for uv
                cat > pyproject.toml << 'EOF'
[project]
name = "mcp-sandbox"
version = "0.1.0"
description = "MCP Code Sandbox"
requires-python = ">=3.8"
dependencies = []

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
EOF
                
                # Create uv virtual environment if it doesn't exist
                if [ ! -d .venv ]; then
                    uv venv
                fi
                
                # Activate virtual environment for future commands
                echo 'source .venv/bin/activate' >> ~/.bashrc
                """
            ], check=True)
            
            self._file_interface = DockerFileInterface(self.container_name)
            self._initialized = True
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to initialize Docker container: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during initialization: {str(e)}")
    
    async def close(self) -> None:
        """Clean up Docker container resources"""
        if not self._initialized:
            return
            
        try:
            # Stop and remove container
            subprocess.run([
                "docker", "stop", self.container_name
            ], capture_output=True, text=True)
            
            subprocess.run([
                "docker", "rm", self.container_name
            ], capture_output=True, text=True)
            
            self._initialized = False
            self._file_interface = None
            
        except subprocess.CalledProcessError:
            # Container might not exist, which is fine
            pass
    
    def run_code(self, code: str) -> ExecutionResult:
        """Execute Python code in the container"""
        if not self._initialized:
            raise RuntimeError("Interpreter not initialized. Call initialize() first.")
        
        try:
            # Create temporary Python file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Copy file to container
                subprocess.run([
                    "docker", "cp", temp_file, f"{self.container_name}:/tmp/exec_code.py"
                ], check=True)
                
                # Execute Python code with uv virtual environment
                result = subprocess.run([
                    "docker", "exec", self.container_name, "bash", "-c",
                    """
                    # Source Nix environment
                    if [ -f ~/.nix-profile/etc/profile.d/nix.sh ]; then
                        source ~/.nix-profile/etc/profile.d/nix.sh
                    fi
                    
                    # Activate virtual environment
                    cd /home/sandbox/workspace
                    source .venv/bin/activate
                    
                    # Execute the Python code
                    python /tmp/exec_code.py
                    """
                ], capture_output=True, text=True, timeout=30)
                
                # Clean up temporary file in container
                subprocess.run([
                    "docker", "exec", self.container_name, "rm", "/tmp/exec_code.py"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    return ExecutionResult(logs=result.stdout)
                else:
                    return ExecutionResult(logs=result.stdout, error=result.stderr)
                    
            finally:
                # Clean up local temporary file
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return ExecutionResult(error="Code execution timed out (30 seconds)")
        except subprocess.CalledProcessError as e:
            return ExecutionResult(error=f"Failed to execute code: {e.stderr}")
        except Exception as e:
            return ExecutionResult(error=f"Unexpected error: {str(e)}")
    
    def run_command(self, command: str) -> ExecutionResult:
        """Run a shell command in the container"""
        if not self._initialized:
            raise RuntimeError("Interpreter not initialized. Call initialize() first.")
        
        try:
            # Execute command with uv virtual environment
            result = subprocess.run([
                "docker", "exec", self.container_name, "bash", "-c",
                f"""
                # Source Nix environment
                if [ -f ~/.nix-profile/etc/profile.d/nix.sh ]; then
                    source ~/.nix-profile/etc/profile.d/nix.sh
                fi
                
                # Activate virtual environment
                cd /home/sandbox/workspace
                source .venv/bin/activate
                
                # Execute the command
                {command}
                """
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return ExecutionResult(logs=result.stdout)
            else:
                return ExecutionResult(logs=result.stdout, error=result.stderr)
                
        except subprocess.TimeoutExpired:
            return ExecutionResult(error="Command execution timed out (30 seconds)")
        except subprocess.CalledProcessError as e:
            return ExecutionResult(error=f"Failed to execute command: {e.stderr}")
        except Exception as e:
            return ExecutionResult(error=f"Unexpected error: {str(e)}")
    
    def install_package(self, package: str) -> ExecutionResult:
        """Install a Python package using uv"""
        return self.run_command(f"uv add {package}")
    
    @property
    def files(self) -> DockerFileInterface:
        """Get the file interface"""
        if not self._initialized or not self._file_interface:
            raise RuntimeError("Interpreter not initialized. Call initialize() first.")
        
        return self._file_interface
    
    @classmethod
    def create(cls, image_name: str = "yingchuan/devenv:latest", 
               container_name: Optional[str] = None,
               workspace_mount: Optional[str] = None) -> 'DockerInterpreter':
        """Factory method to create an interpreter instance"""
        return cls(image_name, container_name, workspace_mount)