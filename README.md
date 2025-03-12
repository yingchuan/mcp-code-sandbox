# MCP Code Sandbox Server

An extensible Message Communication Protocol (MCP) server that provides secure code execution capabilities in isolated sandbox environments. This server follows the MCP standard, making it compatible with Claude for Desktop and other MCP clients.

## Features

- Create isolated sandbox environments for code execution
- Execute Python code securely
- Perform file operations (listing, reading, writing)
- Install Python packages in the sandbox
- Extensible architecture with abstracted code interpreter interface
- Modular design with clean separation of concerns

## Architecture

The server is built with a modular, extensible architecture:

### Core Components

- **Abstract Interpreter Interface**: Allows different code execution backends to be integrated
- **Sandbox Administration**: Tools for creating and managing sandbox environments
- **Code Execution**: Tools for running code and installing packages
- **File Operations**: Tools for managing files within sandboxes

### Project Structure

```
├── src/
│   └── sandbox/
│       ├── __pycache__/
│       ├── e2b/
│       │   ├── __pycache__/
│       │   ├── __init__.py
│       │   ├── e2b_file_interface.py
│       │   └── e2b_interpreter.py
│       ├── __init__.py
│       ├── code_interpreter.py
│       ├── file_interface.py
│       └── interpreter_factory.py
├── tools/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── code_execution_tools.py
│   ├── file_tools.py
│   └── sandbox_tools.py
├── main.py
├── .env
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

## Prerequisites

- Python 3.10 or higher
- E2B API key (for the default E2B interpreter)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/mcp-code-sandbox.git
   cd mcp-code-sandbox
   ```

2. Set up a virtual environment:
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Or using uv (recommended)
   uv init
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   # Using pip
   pip install fastmcp python-dotenv e2b-code-interpreter
   
   # Or using uv
   uv add fastmcp python-dotenv e2b-code-interpreter
   ```

4. Configure environment variables:
   ```
   # Create a .env file with the following variables
   E2B_API_KEY=your_e2b_api_key_here
   INTERPRETER_TYPE=e2b  # Default, can be changed to other implemented interpreters
   ```

## Usage

### Running the Server Standalone

You can run the server directly from the command line:

```bash
python main.py
```

This will start the server using the stdio transport, making it compatible with Claude for Desktop.

### Using with Claude for Desktop

1. Make sure you have the latest version of Claude for Desktop installed

2. Open your Claude for Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

3. Add your code sandbox server configuration:
   ```json
   {
     "mcpServers": {
       "code-sandbox": {
         "command": "python",
         "args": [
           "/ABSOLUTE/PATH/TO/main.py"
         ]
       }
     }
   }
   ```

   Or if you're using `uv`:
   ```json
   {
     "mcpServers": {
       "code-sandbox": {
         "command": "uv",
         "args": [
           "--directory",
           "/ABSOLUTE/PATH/TO/PROJECT_DIRECTORY",
           "run",
           "main.py"
         ]
       }
     }
   }
   ```

4. Save the file and restart Claude for Desktop

## Available Tools

The server provides the following tools:

### Sandbox Administration
- **create_sandbox**: Create a new sandbox environment
- **close_sandbox**: Close and clean up a sandbox
- **get_sandbox_status**: Check status of sandboxes

### Code Execution
- **execute_code**: Run Python code in a sandbox
- **install_package**: Install a Python package
- **create_run_close**: All-in-one tool that creates a sandbox, runs code, and cleans up

### File Operations
- **list_files**: List files in the sandbox
- **read_file**: Read the contents of a file
- **write_file**: Write content to a file
- **upload_file**: Upload a file to the sandbox

## Extending with New Interpreters

The system is designed to be extensible. To add a new code interpreter:

1. Create a new directory under `src/sandbox/` for your interpreter implementation
2. Implement the interfaces defined in `src/sandbox/code_interpreter.py` and `src/sandbox/file_interface.py`
3. Add the new interpreter type to the `src/sandbox/interpreter_factory.py`
4. Configure the environment variable `INTERPRETER_TYPE` to your new interpreter

Example of implementing a new interpreter:

```python
# src/sandbox/my_backend/my_interpreter.py
from src.sandbox.code_interpreter import CodeInterpreter, ExecutionResult
from src.sandbox.file_interface import FileInterface

class MyFileInterface(FileInterface):
    # Implement the required methods
    
class MyInterpreter(CodeInterpreter):
    # Implement the required methods

# Update src/sandbox/interpreter_factory.py to include your new interpreter
```

## Module Descriptions

### Sandbox Core (`src/sandbox/`)
- `code_interpreter.py`: Abstract base class for code interpreters
- `file_interface.py`: Abstract interface for file operations
- `interpreter_factory.py`: Factory for creating code interpreter instances

### E2B Implementation (`src/sandbox/e2b/`)
- `e2b_interpreter.py`: E2B implementation of the code interpreter
- `e2b_file_interface.py`: E2B implementation of file operations

### Tools (`tools/`)
- `sandbox_tools.py`: Tools for sandbox administration
- `code_execution_tools.py`: Tools for code execution
- `file_tools.py`: Tools for file operations

### Main Application
- `main.py`: Main application entry point

## Troubleshooting

If you encounter issues:

- Make sure you have the correct API key for your chosen interpreter
- Check the logs for detailed error messages
- Verify that all required packages are installed
- Ensure Claude for Desktop is configured with the correct path to your script

## Security Considerations

- The code execution happens in sandboxed environments for safety
- Do not use this server to execute untrusted code in production environments
- The server does not currently implement authentication - it should only be used in trusted environments

## License

[MIT License](LICENSE)