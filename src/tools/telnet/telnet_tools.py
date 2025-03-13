# src/tools/telnet/telnet_tools.py
"""
Telnet client tools for MCP
Provides telnet client capabilities through the MCP interface using telnetlib3.
"""
import logging
import asyncio
import uuid
import telnetlib3
from typing import Dict, Any, Optional, List

# logger
logger = logging.getLogger('telnet-tools')

class TelnetTools:
    """Telnet client tools using telnetlib3"""
    
    def __init__(self, active_sandboxes=None):
        """Initialize the telnet tools
        
        Args:
            active_sandboxes: Dictionary of active sandbox instances (optional)
        """
        self.active_connections = {}  # Dictionary to store active telnet connections
        self.active_sandboxes = active_sandboxes or {}
    
    def register_tools(self, mcp):
        """Register all telnet tools with the MCP server"""
        
        @mcp.tool()
        async def connect(host: str, port: int, timeout: int = 30) -> Dict[str, Any]:
            """Connect to a telnet server
            
            Args:
                host: The hostname or IP address of the telnet server
                port: The port to connect to
                timeout: Connection timeout in seconds
                
            Returns:
                A dictionary containing connection information and initial response
            """
            try:
                # Create a unique session ID for this connection
                session_id = str(uuid.uuid4())
                
                # Connect to the telnet server
                reader, writer = await asyncio.wait_for(
                    telnetlib3.open_connection(host, port),
                    timeout=timeout
                )
                
                # Read initial response
                initial_response = await asyncio.wait_for(reader.read(1024), timeout=5)
                
                # Store the connection
                self.active_connections[session_id] = {
                    'reader': reader,
                    'writer': writer,
                    'host': host,
                    'port': port
                }
                
                return {
                    'session_id': session_id,
                    'connected': True,
                    'host': host,
                    'port': port,
                    'initial_response': initial_response
                }
            except Exception as e:
                logger.error(f"Error connecting to {host}:{port}: {str(e)}")
                return {
                    'connected': False,
                    'error': str(e)
                }
        
        @mcp.tool()
        async def send_command(session_id: str, command: str, timeout: int = 10) -> Dict[str, Any]:
            """Send a command to the telnet server
            
            Args:
                session_id: The session ID returned by the connect function
                command: The command to send
                timeout: Timeout in seconds for waiting for a response
                
            Returns:
                A dictionary containing the server's response
            """
            if session_id not in self.active_connections:
                return {
                    'success': False,
                    'error': f"No active connection with session ID {session_id}"
                }
            
            connection = self.active_connections[session_id]
            
            try:
                reader = connection['reader']
                writer = connection['writer']
                
                # Send the command
                writer.write(f"{command}\n")
                await writer.drain()
                
                # Read the response with timeout
                response = await asyncio.wait_for(reader.read(4096), timeout=timeout)
                
                return {
                    'success': True,
                    'response': response
                }
            except Exception as e:
                logger.error(f"Error sending command: {str(e)}")
                return {
                    'success': False,
                    'error': str(e)
                }
        
        @mcp.tool()
        async def disconnect(session_id: str) -> Dict[str, Any]:
            """Disconnect from a telnet server
            
            Args:
                session_id: The session ID returned by the connect function
                
            Returns:
                A dictionary indicating success or failure
            """
            if session_id not in self.active_connections:
                return {
                    'success': False,
                    'error': f"No active connection with session ID {session_id}"
                }
            
            connection = self.active_connections[session_id]
            
            try:
                writer = connection['writer']
                # Close the writer
                writer.close()
                
                # Safely handle wait_closed if it exists, otherwise use a small delay
                try:
                    if hasattr(writer, 'wait_closed') and callable(writer.wait_closed):
                        await writer.wait_closed()
                    else:
                        # Small delay to allow the close operation to complete
                        await asyncio.sleep(0.1)
                except Exception as e:
                    logger.warning(f"Non-critical error during wait_closed: {str(e)}")
                    # Continue with cleanup regardless of this error
                
                # Always clean up the connection from our dictionary
                del self.active_connections[session_id]
                
                return {
                    'success': True,
                    'message': f"Connection {session_id} closed successfully"
                }
            except Exception as e:
                logger.error(f"Error disconnecting: {str(e)}")
                # Try to clean up the connection from our dictionary even if there was an error
                try:
                    del self.active_connections[session_id]
                except:
                    pass
                
                return {
                    'success': False,
                    'error': str(e)
                }
        
        @mcp.tool()
        async def list_connections() -> Dict[str, Any]:
            """List all active telnet connections
            
            Returns:
                A dictionary containing information about all active connections
            """
            connections = []
            for session_id, connection in self.active_connections.items():
                connections.append({
                    'session_id': session_id,
                    'host': connection['host'],
                    'port': connection['port']
                })
            
            return {
                'count': len(connections),
                'connections': connections
            }
        
        # Return the registered tools
        return {
            "connect": connect,
            "send_command": send_command,
            "disconnect": disconnect,
            "list_connections": list_connections
        }