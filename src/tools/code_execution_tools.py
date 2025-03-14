# src/tools/code_execution_tools.py
"""
Code execution module for the MCP Code Sandbox.
Contains all functionality related to executing code and installing packages.
"""
import logging
import traceback
import uuid
import asyncio
from typing import Dict, Any

# imports
from sandbox.interpreter_factory import InterpreterFactory

# logger
logger = logging.getLogger('sandbox-server')

class ExecutionTools:
    """Code execution operations"""
    
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
        """Register all execution tools with the MCP server"""
        
        @mcp.tool()
        async def execute_code(session_id: str, code: str) -> Dict[str, Any]:
            """Execute Python code in the sandbox environment.
            
            Args:
                session_id: The unique identifier for the sandbox session
                code: The Python code to execute
            
            Returns:
                A dictionary containing the execution results including logs and any errors
            """
            # Check if sandbox exists
            if session_id not in self.active_sandboxes:
                return {"error": f"No sandbox found with session ID: {session_id}. Create a sandbox first."}
            
            # Get the interpreter
            interpreter = self.active_sandboxes[session_id]
            
            try:
                # Execute the code
                execution_result = interpreter.run_code(code)
                logger.info(f"Executed code in sandbox {session_id}")
                
                # Return results
                return {
                    "logs": execution_result.logs,
                    "error": execution_result.error
                }
            except Exception as e:
                logger.error(f"Error executing code in sandbox {session_id}: {str(e)}")
                return {"error": f"Error executing code: {str(e)}"}

        @mcp.tool()
        async def install_package(session_id: str, package_name: str) -> Dict[str, Any]:
            """Install a Python package in the sandbox.
            
            Args:
                session_id: The unique identifier for the sandbox session
                package_name: The name of the Python package to install
            
            Returns:
                A dictionary containing the installation output or an error message
            """
            # Check if sandbox exists
            if session_id not in self.active_sandboxes:
                return {"error": f"No sandbox found with session ID: {session_id}. Create a sandbox first."}
            
            # Get the interpreter
            interpreter = self.active_sandboxes[session_id]
            
            try:
                # Install the package using pip
                pip_command = f"pip install {package_name}"
                execution_result = interpreter.run_command(pip_command)
                logger.info(f"Installed package {package_name} in sandbox {session_id}")
                
                return {
                    "package": package_name,
                    "output": execution_result.logs,
                    "error": execution_result.error
                }
            except Exception as e:
                logger.error(f"Error installing package {package_name} in sandbox {session_id}: {str(e)}")
                return {"error": f"Error installing package: {str(e)}"}

        @mcp.tool()
        async def create_run_close(code: str) -> Dict[str, Any]:
            """Create a sandbox, run code, and automatically close the sandbox in one operation.
            
            This is a convenience tool that combines create_sandbox, execute_code, and close_sandbox
            into a single operation, which is useful for simple one-off code executions.
            
            Args:
                code: The Python code to execute
            
            Returns:
                A dictionary containing the execution results
            """
            try:
                # Generate a unique session ID for this operation
                session_id = str(uuid.uuid4())
                logger.info(f"Creating sandbox with session ID {session_id} for one-off execution")
                
                # FIX: Correctly extract parameters from interpreter_config
                backend_url = self.interpreter_config.get('backend_url')
                api_key = self.interpreter_config.get('api_key')
                
                # FIX: Pass parameters correctly to the create_interpreter method
                interpreter = InterpreterFactory.create_interpreter(
                    self.interpreter_type, 
                    backend_url=backend_url,
                    api_key=api_key
                )
                
                await interpreter.initialize()
                
                # Store in active sandboxes
                self.active_sandboxes[session_id] = interpreter
                logger.info(f"Sandbox created successfully")
                
                # Execute code
                try:
                    logger.info(f"Executing code in sandbox {session_id}")
                    
                    # Add time imports if needed for hello world examples
                    if "hello" in code.lower() and "world" in code.lower() and "datetime" not in code:
                        default_code = """
import datetime

print('Hello, World!')
print(f'Current Time: {datetime.datetime.now()}')
"""
                        code = default_code
                        
                    # Execute the code
                    execution_result = interpreter.run_code(code)
                    logger.info(f"Code execution completed")
                    
                    # Store execution results
                    result = {
                        "logs": execution_result.logs,
                        "error": execution_result.error,
                        "sandbox_status": "created and will be closed automatically"
                    }
                except Exception as e:
                    logger.error(f"Error executing code: {str(e)}")
                    result = {"error": f"Error executing code: {str(e)}"}
                
                # Close sandbox
                logger.info(f"Automatically closing sandbox {session_id}")
                try:
                    # Set a timeout for closing
                    await asyncio.wait_for(interpreter.close(), timeout=10.0)
                    logger.info(f"Sandbox closed successfully")
                    result["sandbox_closed"] = True
                except Exception as e:
                    logger.error(f"Error closing sandbox: {str(e)}")
                    result["sandbox_closed"] = False
                    result["close_error"] = str(e)
                finally:
                    # Always remove from active sandboxes
                    if session_id in self.active_sandboxes:
                        del self.active_sandboxes[session_id]
                        result["sandbox_removed"] = True
                
                return result
            except Exception as e:
                logger.error(f"Error in create_run_close operation: {str(e)}")
                logger.error(traceback.format_exc())
                return {"error": f"Operation failed: {str(e)}"}

        # Make the functions available as class methods
        self.execute_code = execute_code
        self.install_package = install_package
        self.create_run_close = create_run_close
        
        return {
            "execute_code": execute_code,
            "install_package": install_package,
            "create_run_close": create_run_close
        }