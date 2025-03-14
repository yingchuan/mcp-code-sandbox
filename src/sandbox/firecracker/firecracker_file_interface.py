# src/sandbox/firecracker/firecracker_file_interface.py
"""
Firecracker implementation of the file interface.
Provides file operations for a remote Firecracker microVM.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional

# imports
from src.sandbox.code_interpreter import FileInterface

# logging
logger = logging.getLogger("firecracker_file_interface")
logger.setLevel(logging.INFO)

class FirecrackerFileInterface(FileInterface):
    """
    Firecracker implementation of the file interface.
    Provides methods for file operations within a remote Firecracker microVM.
    """
    def __init__(self, client, microvm_id: str) -> None:
        """
        Initialize the file interface.

        Args:
            client: An instance of FirecrackerClient.
            microvm_id (str): The ID of the microVM to perform file operations on.
        """
        self.client = client
        self.microvm_id = microvm_id
        logger.info("FirecrackerFileInterface initialized for microVM: %s", self.microvm_id)

    def list(self, path: str) -> List[Dict[str, Any]]:
        """
        List files in the specified path within the microVM.

        Args:
            path (str): The directory path to list.

        Returns:
            List[Dict[str, Any]]: A list of file metadata dictionaries.
        """
        logger.info("Listing files in path: %s for microVM: %s", path, self.microvm_id)
        payload = {
            "microvm_id": self.microvm_id,
            "action": "run_command",
            "command": f"ls -la {path}"
        }
        result = self._run_async(self._list_files(path, payload))
        return self._parse_ls_output(result)

    def read(self, file_path: str) -> str:
        """
        Read the content of a file within the microVM.

        Args:
            file_path (str): The path of the file to read.

        Returns:
            str: The content of the file.
        """
        logger.info("Reading file: %s from microVM: %s", file_path, self.microvm_id)
        payload = {
            "microvm_id": self.microvm_id,
            "action": "run_command",
            "command": f"cat {file_path}"
        }
        result = self._run_async(self._read_file(file_path, payload))
        return result

    def write(self, file_path: str, content: str) -> None:
        """
        Write content to a file within the microVM.

        Args:
            file_path (str): The path of the file to write to.
            content (str): The content to write to the file.
        """
        logger.info("Writing to file: %s in microVM: %s", file_path, self.microvm_id)
        # Use Python to write to ensure proper escaping
        escaped_content = content.replace('"', '\\"')
        code = f"""
with open("{file_path}", "w") as f:
    f.write("{escaped_content}")
"""
        payload = {
            "microvm_id": self.microvm_id,
            "action": "run_code",
            "code": code
        }
        self._run_async(self._write_file(file_path, content, payload))

    def _run_async(self, coro):
        """
        Run an async coroutine synchronously.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    async def _list_files(self, path: str, payload: Dict[str, Any]) -> str:
        """
        Execute the list files command in the microVM.
        """
        response = await self.client.run_command(payload)
        return response.text

    async def _read_file(self, file_path: str, payload: Dict[str, Any]) -> str:
        """
        Execute the read file command in the microVM.
        """
        response = await self.client.run_command(payload)
        return response.text

    async def _write_file(self, file_path: str, content: str, payload: Dict[str, Any]) -> None:
        """
        Execute the write file command in the microVM.
        """
        await self.client.run_code(payload)

    def _parse_ls_output(self, ls_output: str) -> List[Dict[str, Any]]:
        """
        Parse the output of 'ls -la' command into a structured format.

        Args:
            ls_output (str): The output of the 'ls -la' command.

        Returns:
            List[Dict[str, Any]]: A list of file metadata dictionaries.
        """
        result = []
        lines = ls_output.strip().split("\n")
        
        # Skip the first line (total)
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 9:
                # Standard format: permissions, links, owner, group, size, month, day, time/year, name
                file_info = {
                    "name": " ".join(parts[8:]),
                    "type": "directory" if parts[0].startswith("d") else "file",
                    "size": int(parts[4]),
                    "permissions": parts[0],
                    "owner": parts[2],
                    "group": parts[3],
                    "modified": f"{parts[5]} {parts[6]} {parts[7]}"
                }
                result.append(file_info)
                
        return result