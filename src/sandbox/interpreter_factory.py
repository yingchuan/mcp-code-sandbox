# src/sandbox/interpreter_factory.py
"""
Factory for creating code interpreter instances.
This provides a unified way to create different interpreter implementations.
"""
from typing import Optional, Dict, Any

# imports
from sandbox.code_interpreter import CodeInterpreter
from sandbox.e2b.e2b_interpreter import E2BInterpreter


class InterpreterFactory:
    """Factory for creating code interpreter instances"""
    
    # Available interpreter types
    INTERPRETER_E2B = "e2b"
    
    @staticmethod
    def create_interpreter(interpreter_type: str, config: Optional[Dict[str, Any]] = None) -> CodeInterpreter:
        """
        Create an interpreter instance of the specified type
        
        Args:
            interpreter_type: The type of interpreter to create
            config: Optional configuration parameters for the interpreter
            
        Returns:
            A code interpreter instance
            
        Raises:
            ValueError: If the interpreter type is not supported
        """
        config = config or {}
        
        if interpreter_type == InterpreterFactory.INTERPRETER_E2B:
            return E2BInterpreter.create(api_key=config.get("api_key"))
        else:
            raise ValueError(f"Unsupported interpreter type: {interpreter_type}")