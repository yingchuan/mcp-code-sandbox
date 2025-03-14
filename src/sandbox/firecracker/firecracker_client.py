# src/sandbox/firecracker/firecracker_client.py
"""
Client for interacting with a remote Firecracker FastAPI server.
Provides methods for spawning, querying, and shutting down microVMs,
as well as executing code and commands within them.
"""
import logging
from typing import Dict, Any, Optional, List
import httpx

# logger
logger = logging.getLogger("firecracker_client")
logger.setLevel(logging.INFO)

class FirecrackerClient:
    """
    Client for interacting with a remote Firecracker FastAPI server.
    """
    def __init__(self, backend_url: str, api_key: Optional[str] = None) -> None:
        """
        Initialize the client with a backend URL and optional API key.
        
        Args:
            backend_url (str): The URL of the remote Firecracker FastAPI server.
                               Example: "http://firecracker-backend.example.com:8080"
            api_key (Optional[str]): An optional API key for authentication.
        """
        self.backend_url = backend_url
        self.api_key = api_key
        self.session = None
        logger.info("FirecrackerClient initialized with backend_url: %s", self.backend_url)

    async def _ensure_session(self) -> None:
        """
        Ensure that an HTTP session exists, creating one if necessary.
        """
        if self.session is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self.session = httpx.AsyncClient(headers=headers)

    async def close(self) -> None:
        """
        Close the HTTP session.
        """
        if self.session:
            await self.session.aclose()
            self.session = None
            logger.info("FirecrackerClient HTTP session closed")

    async def spawn_microvm(self) -> Dict[str, Any]:
        """
        Spawn a new microVM via a remote REST call.
        
        Returns:
            Dict[str, Any]: Response containing the microvm_id and other details.
        """
        await self._ensure_session()
        endpoint = f"{self.backend_url}/microvm/spawn"
        
        logger.info("Sending request to spawn a new microVM at: %s", endpoint)
        response = await self.session.post(endpoint)
        response.raise_for_status()
        result = response.json()
        logger.info("MicroVM spawn response: %s", result)
        return result

    async def shutdown_microvm(self, microvm_id: str) -> Dict[str, Any]:
        """
        Shut down a specific microVM via a remote REST call.
        
        Args:
            microvm_id (str): The unique identifier of the microVM to shut down.
        
        Returns:
            Dict[str, Any]: Response indicating success or failure.
        """
        await self._ensure_session()
        endpoint = f"{self.backend_url}/microvm/shutdown"
        payload = {"microvm_id": microvm_id}
        
        logger.info("Sending request to shut down microVM %s at: %s", microvm_id, endpoint)
        response = await self.session.post(endpoint, json=payload)
        response.raise_for_status()
        result = response.json()
        logger.info("MicroVM shutdown response: %s", result)
        return result

    async def run_code(self, payload: Dict[str, Any]) -> httpx.Response:
        """
        Execute Python code in a specific microVM via a remote REST call.
        
        Args:
            payload (Dict[str, Any]): A dictionary containing:
                - microvm_id: The unique identifier of the microVM.
                - code: The Python code to execute.
                - Optional additional parameters.
        
        Returns:
            httpx.Response: The response from the server.
        """
        await self._ensure_session()
        endpoint = f"{self.backend_url}/microvm/run_code"
        
        microvm_id = payload.get("microvm_id")
        logger.info("Sending request to run code in microVM %s at: %s", microvm_id, endpoint)
        response = await self.session.post(endpoint, json=payload)
        response.raise_for_status()
        return response

    async def run_command(self, payload: Dict[str, Any]) -> httpx.Response:
        """
        Execute a shell command in a specific microVM via a remote REST call.
        
        Args:
            payload (Dict[str, Any]): A dictionary containing:
                - microvm_id: The unique identifier of the microVM.
                - command: The shell command to execute.
                - Optional additional parameters.
        
        Returns:
            httpx.Response: The response from the server.
        """
        await self._ensure_session()
        endpoint = f"{self.backend_url}/microvm/run_command"
        
        microvm_id = payload.get("microvm_id")
        logger.info("Sending request to run command in microVM %s at: %s", microvm_id, endpoint)
        response = await self.session.post(endpoint, json=payload)
        response.raise_for_status()
        return response

    async def list_microvms(self) -> List[Dict[str, Any]]:
        """
        List all active microVMs via a remote REST call.
        
        Returns:
            List[Dict[str, Any]]: A list of active microVMs and their details.
        """
        await self._ensure_session()
        endpoint = f"{self.backend_url}/microvm/list"
        
        logger.info("Sending request to list active microVMs at: %s", endpoint)
        response = await self.session.get(endpoint)
        response.raise_for_status()
        result = response.json()
        logger.info("MicroVM list response: %s", result)
        return result

    async def get_microvm_status(self, microvm_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific microVM via a remote REST call.
        
        Args:
            microvm_id (str): The unique identifier of the microVM.
        
        Returns:
            Dict[str, Any]: The status and details of the microVM.
        """
        await self._ensure_session()
        endpoint = f"{self.backend_url}/microvm/status"
        params = {"microvm_id": microvm_id}
        
        logger.info("Sending request to get status of microVM %s at: %s", microvm_id, endpoint)
        response = await self.session.get(endpoint, params=params)
        response.raise_for_status()
        result = response.json()
        logger.info("MicroVM status response: %s", result)
        return result