# src/main.py
"""
MCP Code Sandbox Server
Provides secure code execution capabilities in an isolated sandbox environment

This server is structured in a modular way with separate modules for:
- Sandbox administration (create/close sandboxes)
- Code execution (run code, install packages)
- File operations (list/read/write files)
- Telnet client (optional, requires telnetlib3)

The system is designed with an abstract interpreter interface that allows
different code execution backends to be used.
"""
import os
import logging
import atexit
import sys
import asyncio
import traceback
from typing import Dict, Any

# imports
from fastmcp import FastMCP 
from dotenv import load_dotenv

# Import our modules
# Import the tools directly from your project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# imports
from sandbox.code_interpreter import CodeInterpreter
from tools.file_tools import FileTools
from tools.sandbox_tools import SandboxTools
from tools.code_execution_tools import ExecutionTools
from tools.telnet.telnet_tools import TelnetTools
from tools.charts.chart_generator import ChartTools


# configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('sandbox-server')

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("code-sandbox")

# Dictionary to store active interpreter instances
active_sandboxes: Dict[str, CodeInterpreter] = {}

# Get interpreter configuration from environment
interpreter_type = os.environ.get("INTERPRETER_TYPE", "e2b")
interpreter_config = {
    "api_key": os.environ.get("E2B_API_KEY")
}

# Initialize tools modules with the chosen interpreter type
sandbox_tools = SandboxTools(active_sandboxes, interpreter_type, interpreter_config)
execution_tools = ExecutionTools(active_sandboxes, interpreter_type, interpreter_config)
file_tools = FileTools(active_sandboxes)
telnet_tools = TelnetTools(active_sandboxes)
chart_tools = ChartTools(active_sandboxes)

# Register all tools with the MCP server
sandbox_tools.register_tools(mcp)
execution_tools.register_tools(mcp)
file_tools.register_tools(mcp)
telnet_tools.register_tools(mcp)
chart_tools.register_tools(mcp)

def cleanup_all_sandboxes():
    """Clean up all active sandboxes on exit"""
    logger.info("Starting cleanup of all active sandboxes")
    
    async def async_cleanup():
        await sandbox_tools.cleanup_all_sandboxes()
    
    # Run the async cleanup in a new event loop
    if active_sandboxes:
        logger.info(f"Cleaning up {len(active_sandboxes)} active sandboxes")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(async_cleanup())
            loop.close()
            logger.info("Sandbox cleanup completed")
        except Exception as e:
            logger.error(f"Error in cleanup process: {str(e)}")
            logger.error(traceback.format_exc())
    else:
        logger.info("No active sandboxes to clean up")

# Register the cleanup function
atexit.register(cleanup_all_sandboxes)

if __name__ == "__main__":
    try:
        logger.info("Starting MCP Code Sandbox Server...")
        logger.info(f"Using interpreter type: {interpreter_type}")
        
        logger.info("Available tools:")
        logger.info("  Sandbox administration: create_sandbox, close_sandbox, get_sandbox_status")
        logger.info("  Code execution: execute_code, install_package, create_run_close")
        logger.info("  File operations: list_files, read_file, write_file, upload_file")
        logger.info("  Telnet: connect, send_command, disconnect, list_connections")
        logger.info("  Chart generation: generate_line_chart, generate_bar_chart, generate_scatter_plot, generate_interactive_chart, generate_heatmap")

        
        # Log API key status (without revealing the key)
        if interpreter_config.get("api_key"):
            logger.info(f"{interpreter_type.upper()} API key found in environment")
        else:
            logger.warning(f"{interpreter_type.upper()} API key not found in environment")
        
        # Run the MCP server using stdio transport for compatibility with Claude for Desktop
        logger.info("Running MCP server with stdio transport")
        mcp.run(transport='stdio')
    except Exception as e:
        # error
        logger.error(f"Error running MCP server: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)