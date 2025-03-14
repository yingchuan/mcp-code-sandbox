# src/sandbox/interpreter_factory.py
"""
Factory for creating code interpreter instances.
This provides a unified way to create different interpreter implementations.
"""
from typing import Optional

# Imports
from src.sandbox.code_interpreter import CodeInterpreter
from src.sandbox.e2b.e2b_interpreter import E2BInterpreter
from src.sandbox.firecracker.firecracker_interpreter import FirecrackerInterpreter


class InterpreterFactory:
    """Factory for creating code interpreter instances"""

    # Available interpreter types
    INTERPRETER_E2B = "e2b"
    INTERPRETER_FIRECRACKER = "firecracker"

    @staticmethod
    def create_interpreter(interpreter_type: str,
                           backend_url: Optional[str] = None,
                           api_key: Optional[str] = None) -> CodeInterpreter:
        """
        Create an interpreter instance of the specified type.
        
        Args:
            interpreter_type: The type of interpreter to create.
            backend_url: The remote backend URL for Firecracker interpreters.
                         Not used for E2B.
            api_key: The API key for authentication.
                     For E2B, this is required; for Firecracker, it is optional.
        
        Returns:
            A code interpreter instance.
        
        Raises:
            ValueError: If the interpreter type is not supported or required parameters are missing.
        """
        if interpreter_type == InterpreterFactory.INTERPRETER_E2B:
            if not api_key:
                raise ValueError("API key must be provided for E2B interpreter.")
            # E2B interpreter is created with an API key.
            return E2BInterpreter.create(api_key=api_key)
        elif interpreter_type == InterpreterFactory.INTERPRETER_FIRECRACKER:
            if not backend_url:
                raise ValueError("Backend URL must be provided for Firecracker interpreter.")
            # Create a Firecracker interpreter using base URL and optional API key.
            return FirecrackerInterpreter.create(backend_url, api_key)
        else:
            raise ValueError(f"Unsupported interpreter type: {interpreter_type}")
