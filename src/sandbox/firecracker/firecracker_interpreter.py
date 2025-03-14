# src/sandbox/firecracker/firecracker_interpreter.py
"""
Firecracker implementation of the code interpreter interface.
This interpreter makes REST calls to a remote Firecracker FastAPI server using FirecrackerClient.
It accepts a backend URL and an optional API key.
It initializes by spawning (or connecting to) a microVM.
"""
import asyncio
import logging
import os
from typing import Optional, Dict, Any

from src.sandbox.code_interpreter import CodeInterpreter, ExecutionResult, FileInterface
from src.sandbox.firecracker.firecracker_client import FirecrackerClient
from src.sandbox.firecracker.firecracker_file_interface import FirecrackerFileInterface

logger = logging.getLogger("firecracker_interpreter")
logger.setLevel(logging.INFO)

class FirecrackerInterpreter(CodeInterpreter):
    """
    Firecracker implementation of the code interpreter interface.
    This interpreter acts as a client to a remote Firecracker FastAPI server using FirecrackerClient.
    It spawns a new microVM on initialization and uses its microvm_id for subsequent operations.
    """
    def __init__(self, backend_url: Optional[str] = None, api_key: Optional[str] = None) -> None:
        """
        Initialize the interpreter.
        
        Args:
            backend_url (Optional[str]): The URL of the remote Firecracker FastAPI server.
                                        If None, will use FIRECRACKER_BACKEND_URL environment variable.
            api_key (Optional[str]): An optional API key for authentication.
                                     If None, will use FIRECRACKER_API_KEY environment variable.
        """
        self.backend_url = backend_url or os.environ.get("FIRECRACKER_BACKEND_URL")
        self.api_key = api_key or os.environ.get("FIRECRACKER_API_KEY")
        
        if not self.backend_url:
            raise ValueError("Missing backend_url in configuration. Either provide it directly or set FIRECRACKER_BACKEND_URL environment variable.")
        
        self._initialized = False
        self.microvm_id = None  # Will store the spawned microVM identifier.
        self._file_interface = None
        
        # Create an instance of FirecrackerClient using the provided backend_url and api_key.
        self.client = FirecrackerClient(self.backend_url, self.api_key)
        logger.info("FirecrackerInterpreter created with backend_url: %s", self.backend_url)

    async def initialize(self) -> None:
        """
        Initialize the interpreter by spawning a microVM via a remote REST call.
        """
        logger.info("Spawning Firecracker microVM via remote REST call at %s...", self.backend_url)
        spawn_result = await self.client.spawn_microvm()
        self.microvm_id = spawn_result.get("microvm_id")
        if not self.microvm_id:
            raise RuntimeError("Failed to spawn microVM: no microvm_id returned.")
        
        # Initialize file interface
        self._file_interface = FirecrackerFileInterface(self.client, self.microvm_id)
        
        self._initialized = True
        logger.info("Firecracker microVM spawned with id: %s", self.microvm_id)

    async def close(self) -> None:
        """
        Shut down the Firecracker microVM via a remote REST call.
        """
        if not self._initialized or not self.microvm_id:
            logger.warning("Interpreter is not initialized or microvm_id is missing; nothing to close.")
            return
        
        logger.info("Shutting down Firecracker microVM with id %s via remote REST call...", self.microvm_id)
        await self.client.shutdown_microvm(self.microvm_id)
        self._initialized = False
        self.microvm_id = None
        self._file_interface = None
        await self.client.close()
        logger.info("Firecracker microVM shut down.")

    def run_code(self, code: str) -> ExecutionResult:
        """
        Execute Python code in the remote Firecracker microVM.
        This method is synchronous; it wraps an async call to send a code execution request.
        """
        if not self._initialized or not self.microvm_id:
            raise RuntimeError("Interpreter not initialized. Call initialize() first.")
        
        payload = {
            "microvm_id": self.microvm_id,
            "code": code
        }
        response = self._run_async(self._run_code_async(payload))
        
        logs = ""
        error = None
        
        try:
            result = response.get("result", {})
            logs = result.get("stdout", "")
            error_output = result.get("stderr", "")
            if error_output:
                error = error_output
        except Exception as e:
            logger.error("Error parsing run_code response: %s", e)
            error = str(e)
        
        return ExecutionResult(
            logs=logs,
            error=error
        )

    def run_command(self, command: str) -> ExecutionResult:
        """
        Execute a shell command in the remote Firecracker microVM.
        This method is synchronous; it wraps an async call to send a command execution request.
        """
        if not self._initialized or not self.microvm_id:
            raise RuntimeError("Interpreter not initialized. Call initialize() first.")
        
        payload = {
            "microvm_id": self.microvm_id,
            "command": command
        }
        response = self._run_async(self._run_command_async(payload))
        
        logs = ""
        error = None
        
        try:
            result = response.get("result", {})
            logs = result.get("stdout", "")
            error_output = result.get("stderr", "")
            if error_output:
                error = error_output
        except Exception as e:
            logger.error("Error parsing run_command response: %s", e)
            error = str(e)
        
        return ExecutionResult(
            logs=logs,
            error=error
        )

    def _run_async(self, coro):
        """
        Synchronously run an async coroutine.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    async def _run_code_async(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run code asynchronously via the client.
        """
        response = await self.client.run_code(payload)
        return response.json()

    async def _run_command_async(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run command asynchronously via the client.
        """
        response = await self.client.run_command(payload)
        return response.json()

    @property
    def files(self) -> FileInterface:
        """
        Get the file interface for the Firecracker microVM.
        
        Returns:
            FileInterface: An interface for file operations within the microVM.
        
        Raises:
            RuntimeError: If the interpreter is not initialized.
        """
        if not self._initialized or not self.microvm_id or not self._file_interface:
            raise RuntimeError("Interpreter not initialized. Call initialize() first.")
        
        return self._file_interface

    @classmethod
    def create(cls, backend_url: Optional[str] = None, api_key: Optional[str] = None) -> "FirecrackerInterpreter":
        """
        Factory method to create a FirecrackerInterpreter instance.
        
        Args:
            backend_url (Optional[str]): The URL of the remote Firecracker FastAPI server.
            api_key (Optional[str]): An optional API key for authentication.
        
        Returns:
            FirecrackerInterpreter: A new instance.
        """
        return cls(backend_url, api_key)