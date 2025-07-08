#!/usr/bin/env python3
"""
Test script for MCP Code Sandbox Docker integration.
"""
import os
import asyncio
import sys

# Set environment for Docker interpreter
os.environ['INTERPRETER_TYPE'] = 'docker'
os.environ['DOCKER_IMAGE_NAME'] = 'yingchuan/devenv:latest'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sandbox.interpreter_factory import InterpreterFactory
from tools.sandbox_tools import SandboxTools
from tools.code_execution_tools import ExecutionTools
from tools.file_tools import FileTools


async def test_mcp_integration():
    """Test MCP tools integration with Docker interpreter"""
    print("Testing MCP Code Sandbox with Docker interpreter...")
    
    # Initialize components
    active_sandboxes = {}
    interpreter_type = "docker"
    interpreter_config = {
        "image_name": "yingchuan/devenv:latest"
    }
    
    # Initialize tools
    sandbox_tools = SandboxTools(active_sandboxes, interpreter_type, interpreter_config)
    execution_tools = ExecutionTools(active_sandboxes, interpreter_type, interpreter_config)
    file_tools = FileTools(active_sandboxes)
    
    try:
        # Test 1: Create sandbox
        print("\n1. Creating sandbox...")
        sandbox_id = await sandbox_tools.create_sandbox()
        print(f"✅ Sandbox created: {sandbox_id}")
        
        # Test 2: Execute code
        print("\n2. Executing Python code...")
        result = await execution_tools.execute_code(
            sandbox_id,
            """
import sys
print(f"Python version: {sys.version}")
print("Hello from MCP Docker sandbox!")

# Test some calculations
numbers = [1, 2, 3, 4, 5]
sum_result = sum(numbers)
print(f"Sum of {numbers} = {sum_result}")
"""
        )
        print(f"✅ Code execution result:")
        print(result.get('logs', ''))
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
        
        # Test 3: File operations
        print("\n3. Testing file operations...")
        
        # Write file
        await file_tools.write_file(sandbox_id, "test.py", """
def greet(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("MCP Docker"))
""")
        print("✅ File written successfully")
        
        # Read file
        content = await file_tools.read_file(sandbox_id, "test.py")
        print(f"✅ File content read: {len(content)} characters")
        
        # List files
        files = await file_tools.list_files(sandbox_id, ".")
        print(f"✅ Files in sandbox: {[f.get('name', 'unknown') for f in files]}")
        
        # Test 4: Execute the file
        print("\n4. Executing the written file...")
        result = await execution_tools.execute_code(sandbox_id, "exec(open('test.py').read())")
        print(f"✅ File execution result:")
        print(result.get('logs', ''))
        
        # Test 5: Install and use package
        print("\n5. Testing package installation...")
        install_result = await execution_tools.install_package(sandbox_id, "requests")
        print(f"📦 Package installation result:")
        print(install_result.get('logs', ''))
        if install_result.get('error'):
            print(f"❌ Install error: {install_result['error']}")
        
        # Test 6: Sandbox status
        print("\n6. Checking sandbox status...")
        status = await sandbox_tools.get_sandbox_status(sandbox_id)
        print(f"✅ Sandbox status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        print("\n7. Cleaning up...")
        try:
            await sandbox_tools.close_sandbox(sandbox_id)
            print("✅ Sandbox closed successfully")
        except Exception as e:
            print(f"❌ Cleanup error: {e}")


if __name__ == "__main__":
    success = asyncio.run(test_mcp_integration())
    if success:
        print("\n🎉 All MCP integration tests passed!")
    else:
        print("\n❌ MCP integration tests failed!")
        sys.exit(1)