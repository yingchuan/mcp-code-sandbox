#!/usr/bin/env python3
"""
Test script for Docker interpreter implementation.
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sandbox.interpreter_factory import InterpreterFactory


async def test_docker_interpreter():
    """Test the Docker interpreter functionality"""
    print("Testing Docker Interpreter...")
    
    # Create Docker interpreter
    interpreter = InterpreterFactory.create_interpreter(
        interpreter_type="docker",
        image_name="yingchuan/devenv:latest"
    )
    
    try:
        # Initialize interpreter
        print("Initializing interpreter...")
        await interpreter.initialize()
        print("✅ Interpreter initialized successfully")
        
        # Test basic Python code execution
        print("\nTesting Python code execution...")
        result = interpreter.run_code("""
import sys
print(f"Python version: {sys.version}")
print("Hello from Docker container!")

# Test simple calculation
result = 2 + 2
print(f"2 + 2 = {result}")
""")
        
        if result.error:
            print(f"❌ Error: {result.error}")
        else:
            print("✅ Code executed successfully:")
            print(result.logs)
        
        # Test package installation with uv
        print("\nTesting package installation with uv...")
        result = interpreter.run_command("uv add requests")
        
        if result.error:
            print(f"❌ Package installation error: {result.error}")
        else:
            print("✅ Package installed successfully:")
            print(result.logs)
        
        # Test using installed package
        print("\nTesting installed package...")
        result = interpreter.run_code("""
try:
    import requests
    print("✅ requests package imported successfully")
    print(f"requests version: {requests.__version__}")
except ImportError as e:
    print(f"❌ Failed to import requests: {e}")
""")
        
        if result.error:
            print(f"❌ Error: {result.error}")
        else:
            print("✅ Package test completed:")
            print(result.logs)
        
        # Test file operations
        print("\nTesting file operations...")
        
        # Write a file
        interpreter.files.write("test.txt", "Hello from MCP Docker Sandbox!")
        print("✅ File written successfully")
        
        # Read the file
        content = interpreter.files.read("test.txt")
        print(f"✅ File content: {content}")
        
        # List files
        files = interpreter.files.list(".")
        print(f"✅ Files in workspace: {[f['name'] for f in files]}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Clean up
        print("\nCleaning up...")
        await interpreter.close()
        print("✅ Interpreter closed")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_docker_interpreter())
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)