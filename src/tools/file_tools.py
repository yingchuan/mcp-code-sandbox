# src/tools/file_tools.py
"""
File operations module for the MCP Code Sandbox.
Contains all file-related tools for the sandbox environment.
"""
import os
import logging
from typing import Dict, Any

# logger
logger = logging.getLogger('sandbox-server')

class FileTools:
    """File operations for sandboxes"""
    
    def __init__(self, active_sandboxes):
        """Initialize with a reference to the active sandboxes dictionary"""
        self.active_sandboxes = active_sandboxes
    
    async def list_files(self, session_id: str, path: str = "/") -> list:
        """List files in the sandbox at the specified path (direct method).
        
        Args:
            session_id: The unique identifier for the sandbox session
            path: The directory path to list files from (default: root directory)
        
        Returns:
            A list of files in the directory
        """
        # Check if sandbox exists
        if session_id not in self.active_sandboxes:
            raise ValueError(f"No sandbox found with session ID: {session_id}. Create a sandbox first.")
        
        # Get the interpreter
        interpreter = self.active_sandboxes[session_id]
        
        try:
            # List files
            files = interpreter.files.list(path)
            return files
        except Exception as e:
            logger.error(f"Error listing files in sandbox {session_id}: {str(e)}")
            raise RuntimeError(f"Error listing files: {str(e)}")

    async def read_file(self, session_id: str, file_path: str) -> str:
        """Read the contents of a file in the sandbox (direct method).
        
        Args:
            session_id: The unique identifier for the sandbox session
            file_path: The path to the file to read
        
        Returns:
            The content of the file as a string
        """
        # Check if sandbox exists
        if session_id not in self.active_sandboxes:
            raise ValueError(f"No sandbox found with session ID: {session_id}. Create a sandbox first.")
        
        # Get the interpreter
        interpreter = self.active_sandboxes[session_id]
        
        try:
            # Read the file
            content = interpreter.files.read(file_path)
            return content
        except Exception as e:
            logger.error(f"Error reading file in sandbox {session_id}: {str(e)}")
            raise RuntimeError(f"Error reading file: {str(e)}")

    async def write_file(self, session_id: str, file_path: str, content: str) -> str:
        """Write content to a file in the sandbox (direct method).
        
        Args:
            session_id: The unique identifier for the sandbox session
            file_path: The path to the file to write
            content: The content to write to the file
        
        Returns:
            A confirmation message indicating the file was written successfully
        """
        # Check if sandbox exists
        if session_id not in self.active_sandboxes:
            raise ValueError(f"No sandbox found with session ID: {session_id}. Create a sandbox first.")
        
        # Get the interpreter
        interpreter = self.active_sandboxes[session_id]
        
        try:
            # Write the file
            interpreter.files.write(file_path, content)
            return f"File written successfully: {file_path}"
        except Exception as e:
            logger.error(f"Error writing file in sandbox {session_id}: {str(e)}")
            raise RuntimeError(f"Error writing file: {str(e)}")

    async def upload_file(self, session_id: str, file_name: str, file_content: str, destination_path: str = "/") -> str:
        """Upload a file to the sandbox (direct method).
        
        Args:
            session_id: The unique identifier for the sandbox session
            file_name: The name of the file to create
            file_content: The content of the file
            destination_path: The directory where the file should be created (default: root directory)
        
        Returns:
            A confirmation message indicating the file was uploaded successfully
        """
        # Check if sandbox exists
        if session_id not in self.active_sandboxes:
            raise ValueError(f"No sandbox found with session ID: {session_id}. Create a sandbox first.")
        
        # Get the interpreter
        interpreter = self.active_sandboxes[session_id]
        
        try:
            # Create full file path
            full_path = os.path.join(destination_path, file_name)
            if not full_path.startswith("/"):
                full_path = "/" + full_path
                
            # Write the file
            interpreter.files.write(full_path, file_content)
            return f"File uploaded successfully: {full_path}"
        except Exception as e:
            logger.error(f"Error uploading file to sandbox {session_id}: {str(e)}")
            raise RuntimeError(f"Error uploading file: {str(e)}")
    
    def register_tools(self, mcp):
        """Register all file tools with the MCP server"""
        
        @mcp.tool()
        async def list_files(session_id: str, path: str = "/") -> Dict[str, Any]:
            """List files in the sandbox at the specified path.
            
            Args:
                session_id: The unique identifier for the sandbox session
                path: The directory path to list files from (default: root directory)
            
            Returns:
                A dictionary containing the file listing or an error message
            """
            try:
                files = await self.list_files(session_id, path)
                return {"path": path, "files": files}
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        async def read_file(session_id: str, file_path: str) -> Dict[str, Any]:
            """Read the contents of a file in the sandbox.
            
            Args:
                session_id: The unique identifier for the sandbox session
                file_path: The path to the file to read
            
            Returns:
                A dictionary containing the file content or an error message
            """
            try:
                content = await self.read_file(session_id, file_path)
                return {"path": file_path, "content": content}
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        async def write_file(session_id: str, file_path: str, content: str) -> Dict[str, Any]:
            """Write content to a file in the sandbox.
            
            Args:
                session_id: The unique identifier for the sandbox session
                file_path: The path to the file to write
                content: The content to write to the file
            
            Returns:
                A dictionary containing a success message or an error message
            """
            try:
                message = await self.write_file(session_id, file_path, content)
                return {"path": file_path, "message": message}
            except Exception as e:
                return {"error": str(e)}

        @mcp.tool()
        async def upload_file(session_id: str, file_name: str, file_content: str, destination_path: str = "/") -> Dict[str, Any]:
            """Upload a file to the sandbox.
            
            Args:
                session_id: The unique identifier for the sandbox session
                file_name: The name of the file to create
                file_content: The content of the file
                destination_path: The directory where the file should be created (default: root directory)
            
            Returns:
                A dictionary containing a success message or an error message
            """
            try:
                message = await self.upload_file(session_id, file_name, file_content, destination_path)
                # Extract the path from the message
                full_path = message.split(": ")[1] if ": " in message else destination_path + "/" + file_name
                return {"path": full_path, "message": message}
            except Exception as e:
                return {"error": str(e)}
                
        return {
            "list_files": list_files,
            "read_file": read_file,
            "write_file": write_file,
            "upload_file": upload_file
        }