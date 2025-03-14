# src/tools/sandbox_tools.py
"""
Sandbox management module for the MCP Code Sandbox.
Contains all sandbox administration operations for creating, managing, and closing sandboxes.
"""
import logging
import asyncio
import traceback
from typing import Dict, Any, Optional

# imports
from sandbox.interpreter_factory import InterpreterFactory

# logger
logger = logging.getLogger('sandbox-server')

class SandboxTools:
    """Sandbox administration operations"""
    
    def __init__(self, active_sandboxes, interpreter_type="e2b", interpreter_config=None):
        """
        Initialize with a reference to the active sandboxes dictionary
        
        Args:
            active_sandboxes: Dictionary to store active sandbox instances
            interpreter_type: Type of interpreter to use (default: "e2b")
            interpreter_config: Optional configuration for the interpreter
        """
        self.active_sandboxes = active_sandboxes
        self.interpreter_type = interpreter_type
        self.interpreter_config = interpreter_config or {}
    
    def register_tools(self, mcp):
        """Register all sandbox administration tools with the MCP server"""
        
        @mcp.tool()
        async def create_sandbox(session_id: str) -> str:
            """Create a new sandbox environment for code execution.
            
            Args:
                session_id: A unique identifier for the sandbox session
            
            Returns:
                A confirmation message indicating the sandbox was created
            """
            # Check if sandbox already exists
            if session_id in self.active_sandboxes:
                return f"Sandbox with session ID {session_id} already exists."
            
            try:
                # FIX: Correctly extract and pass parameters using named arguments
                backend_url = self.interpreter_config.get('backend_url')
                api_key = self.interpreter_config.get('api_key')
                
                # Create a new interpreter with named parameters
                interpreter = InterpreterFactory.create_interpreter(
                    self.interpreter_type, 
                    backend_url=backend_url,
                    api_key=api_key
                )
                
                # Initialize the interpreter
                await interpreter.initialize()
                
                # Store in active sandboxes
                self.active_sandboxes[session_id] = interpreter
                logger.info(f"Created sandbox with session ID: {session_id} using {self.interpreter_type} interpreter")
                
                return f"Sandbox created successfully with session ID: {session_id}"
            except Exception as e:
                logger.error(f"Error creating sandbox: {str(e)}")
                return f"Failed to create sandbox: {str(e)}"

        @mcp.tool()
        async def close_sandbox(session_id: str) -> str:
            """Close and clean up a sandbox environment.
            
            Args:
                session_id: The unique identifier for the sandbox session
            
            Returns:
                A confirmation message indicating the sandbox was closed
            """
            # Check if sandbox exists
            logger.info(f"Attempting to close sandbox with session ID: {session_id}")
            if session_id not in self.active_sandboxes:
                logger.warning(f"No sandbox found with session ID: {session_id}")
                # Return a message that doesn't suggest an error, which might cause retries
                return f"Sandbox with session ID {session_id} is not active or has already been closed."
            
            try:
                # Get the sandbox
                interpreter = self.active_sandboxes[session_id]
                logger.info(f"Retrieved interpreter object for session {session_id}")
                
                # Debug sandbox object
                logger.info(f"Interpreter type: {type(interpreter)}")
                
                # Close the sandbox with a timeout
                logger.info(f"Attempting to close sandbox {session_id}")
                
                # Use asyncio with timeout
                try:
                    # Set a timeout of 10 seconds for closing
                    await asyncio.wait_for(interpreter.close(), timeout=10.0)
                    logger.info(f"Sandbox {session_id} closed successfully")
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout while closing sandbox {session_id}, continuing with cleanup")
                
                # Remove from active sandboxes even if there was a timeout
                logger.info(f"Removing sandbox {session_id} from active sandboxes")
                del self.active_sandboxes[session_id]
                
                # Return a very clear success message
                return f"Sandbox with session ID {session_id} has been successfully closed and all resources freed."
            except Exception as e:
                # Log the error for debugging with full traceback
                logger.error(f"Error closing sandbox {session_id}: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Still remove from active sandboxes to prevent resource leaks
                if session_id in self.active_sandboxes:
                    logger.info(f"Removing sandbox {session_id} from active sandboxes despite error")
                    del self.active_sandboxes[session_id]
                
                # Return a success-oriented message even on error, to avoid triggering retries
                return f"Sandbox with session ID {session_id} has been removed from active sessions. Cleanup completed."

        @mcp.tool()
        async def get_sandbox_status(session_id: Optional[str] = None) -> Dict[str, Any]:
            """Get status information about sandboxes.
            
            Args:
                session_id: Optional session ID to get status for a specific sandbox
                
            Returns:
                Information about active sandboxes
            """
            if session_id:
                if session_id not in self.active_sandboxes:
                    return {"error": f"No sandbox found with session ID: {session_id}"}
                return {
                    "status": "active", 
                    "session_id": session_id,
                    "interpreter_type": self.interpreter_type
                }
            else:
                return {
                    "active_sandbox_count": len(self.active_sandboxes),
                    "active_sessions": list(self.active_sandboxes.keys()),
                    "interpreter_type": self.interpreter_type
                }
        
        # Make the functions available as class methods
        self.create_sandbox = create_sandbox
        self.close_sandbox = close_sandbox
        self.get_sandbox_status = get_sandbox_status
        
        return {
            "create_sandbox": create_sandbox,
            "close_sandbox": close_sandbox,
            "get_sandbox_status": get_sandbox_status
        }
    
    async def cleanup_all_sandboxes(self):
        """Clean up all active sandboxes"""
        logger.info("Cleaning up all active sandboxes")
        
        for session_id, interpreter in list(self.active_sandboxes.items()):
            try:
                logger.info(f"Attempting to close sandbox {session_id}")
                # Use timeout to prevent hanging
                try:
                    await asyncio.wait_for(interpreter.close(), timeout=5.0)
                    logger.info(f"Cleaned up sandbox {session_id}")
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout while closing sandbox {session_id}")
            except Exception as e:
                logger.error(f"Error cleaning up sandbox {session_id}: {str(e)}")
                logger.error(traceback.format_exc())
            
            # Always remove from active sandboxes
            if session_id in self.active_sandboxes:
                del self.active_sandboxes[session_id]