# Docker Interpreter Setup

This guide explains how to use the Docker interpreter backend with MCP Code Sandbox.

## Prerequisites

1. **Docker installed and running**
2. **dev.bootstrap devenv image built** (from the dev.bootstrap project)
3. **MCP Code Sandbox dependencies installed**

## Quick Start

1. **Copy the Docker environment configuration:**
   ```bash
   cp .env.docker .env
   ```

2. **Ensure the devenv image is built:**
   ```bash
   # From the dev.bootstrap directory
   ./dev-env build
   ```

3. **Test the Docker interpreter:**
   ```bash
   python test_docker_interpreter.py
   ```

4. **Run the MCP server:**
   ```bash
   python src/main.py
   ```

## Configuration

The Docker interpreter can be configured through environment variables:

- `INTERPRETER_TYPE=docker` - Use Docker interpreter
- `DOCKER_IMAGE_NAME` - Docker image to use (default: `yingchuan/devenv:latest`)
- `DOCKER_WORKSPACE_MOUNT` - Host path for workspace mounting (optional)
- `DOCKER_CONTAINER_NAME_PREFIX` - Container name prefix (optional)

## Features

### Security
- **Container isolation**: Each sandbox runs in its own Docker container
- **Network isolation**: Containers run with `--network none` by default
- **Filesystem isolation**: Sandboxed filesystem access
- **No persistent state**: Containers are destroyed after use

### Python Environment
- **uv package manager**: Fast Python package installation
- **Virtual environment**: Isolated Python environment per sandbox
- **Modern Python**: Uses Python 3.12+ from the devenv image

### Development Tools
- **Full dev environment**: Includes all tools from your devenv image
- **Nix package manager**: Access to extensive package collection
- **File operations**: Read/write files within the sandbox

## Usage Examples

### Basic Code Execution
```python
from sandbox.interpreter_factory import InterpreterFactory

# Create interpreter
interpreter = InterpreterFactory.create_interpreter("docker")

# Initialize
await interpreter.initialize()

# Execute code
result = interpreter.run_code("print('Hello from Docker!')")
print(result.logs)

# Clean up
await interpreter.close()
```

### Package Installation
```python
# Install a package
result = interpreter.run_command("uv add requests")

# Use the package
result = interpreter.run_code("""
import requests
response = requests.get('https://httpbin.org/json')
print(response.json())
""")
```

### File Operations
```python
# Write a file
interpreter.files.write("hello.py", "print('Hello from file!')")

# Read a file
content = interpreter.files.read("hello.py")

# List files
files = interpreter.files.list(".")
```

## Architecture

The Docker interpreter implementation consists of:

1. **DockerInterpreter**: Main interpreter class that manages Docker containers
2. **DockerFileInterface**: File operations within containers
3. **Integration**: Seamless integration with your existing dev.bootstrap setup

### Container Lifecycle
1. Container is created with workspace volume mount
2. Python virtual environment is set up with uv
3. Code/commands are executed within the container
4. Container is destroyed when sandbox is closed

### Security Model
- Containers run with minimal privileges
- No network access (configurable)
- Filesystem access limited to workspace
- Automatic cleanup on exit

## Troubleshooting

### Common Issues

**Container fails to start:**
- Ensure Docker is running
- Check if the devenv image exists: `docker images | grep yingchuan/devenv`
- Build the image: `./dev-env build`

**Package installation fails:**
- Network access might be disabled
- Check if the container has internet connectivity
- Consider pre-installing packages in the base image

**File operations fail:**
- Check workspace mount permissions
- Ensure the workspace directory exists on the host

### Debug Mode
Set `DOCKER_DEBUG=1` to enable verbose logging:
```bash
DOCKER_DEBUG=1 python src/main.py
```

## Comparison with Other Interpreters

| Feature | Docker | E2B | Firecracker |
|---------|--------|-----|-------------|
| Security | High | High | Highest |
| Performance | Good | Good | Excellent |
| Setup | Simple | API Key | Complex |
| Customization | High | Medium | High |
| Cost | Free | Paid | Free |

## Contributing

To extend the Docker interpreter:

1. Modify `src/sandbox/docker/docker_interpreter.py`
2. Update configuration in `src/sandbox/interpreter_factory.py`
3. Add tests in `tests/sandbox/docker/`
4. Update documentation

## License

Same as the main MCP Code Sandbox project.