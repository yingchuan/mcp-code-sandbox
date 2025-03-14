# Direct test for chart tools functionality
import os
import sys
import asyncio
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('chart-test')

# Import the tools directly from your project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sandbox.code_interpreter import CodeInterpreter
from sandbox.interpreter_factory import InterpreterFactory
from tools.charts.chart_generator import ChartTools

async def test_chart_tools():
    """Test chart tools directly by creating an interpreter and using the tools"""
    
    # Dictionary to store active interpreter instances
    active_sandboxes: Dict[str, CodeInterpreter] = {}
    session_id = "chart_test"
    
    try:
        # Step 1: Create an interpreter instance manually
        logger.info("Creating interpreter instance...")
        interpreter_type = "e2b"  # or whatever you're using
        interpreter_config = {"api_key": os.environ.get("E2B_API_KEY")}
        
        # Create interpreter
        interpreter = InterpreterFactory.create_interpreter(
            interpreter_type, 
            interpreter_config
        )
        
        # Initialize the interpreter
        await interpreter.initialize()
        
        # Store in active sandboxes
        active_sandboxes[session_id] = interpreter
        logger.info(f"Created interpreter with session ID: {session_id}")
        
        # Step 2: Initialize the chart tools
        chart_tools = ChartTools(active_sandboxes)
        
        # Step 3: Prepare test data
        logger.info("Preparing test data...")
        monthly_data = [
            {"month": "Jan", "sales": 120, "expenses": 80, "profit": 40},
            {"month": "Feb", "sales": 150, "expenses": 90, "profit": 60},
            {"month": "Mar", "sales": 180, "expenses": 95, "profit": 85},
            {"month": "Apr", "sales": 170, "expenses": 100, "profit": 70},
            {"month": "May", "sales": 210, "expenses": 110, "profit": 100},
            {"month": "Jun", "sales": 250, "expenses": 120, "profit": 130},
        ]
        
        # Step 4: Test line chart generation
        logger.info("Generating line chart...")
        line_chart_result = await chart_tools.generate_line_chart(
            session_id=session_id,
            data=monthly_data,
            x_key="month",
            y_keys=["sales", "expenses", "profit"],
            title="Monthly Financial Performance",
            x_label="Month",
            y_label="Amount ($)",
            save_path="/tmp/monthly_performance.png"
        )
        
        if "error" in line_chart_result and line_chart_result["error"]:
            logger.error(f"Error generating line chart: {line_chart_result['error']}")
        else:
            logger.info("Line chart generated successfully!")
            logger.info(f"Chart saved to: {line_chart_result.get('file_path')}")
            has_base64 = "base64_image" in line_chart_result and line_chart_result["base64_image"]
            logger.info(f"Base64 image data retrieved: {has_base64}")
        
        # Step 5: Test bar chart generation
        logger.info("Generating bar chart...")
        bar_chart_result = await chart_tools.generate_bar_chart(
            session_id=session_id,
            data=monthly_data,
            category_key="month",
            value_keys=["sales", "expenses", "profit"],
            title="Monthly Financial Comparison",
            x_label="Month",
            y_label="Amount ($)",
            save_path="/tmp/monthly_comparison.png"
        )
        
        if "error" in bar_chart_result and bar_chart_result["error"]:
            logger.error(f"Error generating bar chart: {bar_chart_result['error']}")
        else:
            logger.info("Bar chart generated successfully!")
        
        # Step 6: Test interactive chart generation
        logger.info("Generating interactive chart...")
        interactive_result = await chart_tools.generate_interactive_chart(
            session_id=session_id,
            chart_type="line",
            data=monthly_data,
            x_key="month",
            y_keys=["sales", "expenses", "profit"],
            title="Interactive Monthly Performance",
            save_path="/tmp/interactive_performance.html"
        )
        
        if "error" in interactive_result and interactive_result["error"]:
            logger.error(f"Error generating interactive chart: {interactive_result['error']}")
        else:
            logger.info("Interactive chart generated successfully!")
            logger.info(f"HTML file saved to: {interactive_result.get('file_path')}")
            html_size = len(interactive_result.get("html_content", "")) if "html_content" in interactive_result else 0
            logger.info(f"HTML content size: {html_size} bytes")
        
        return {
            "line_chart": line_chart_result,
            "bar_chart": bar_chart_result,
            "interactive_chart": interactive_result
        }
        
    except Exception as e:
        logger.error(f"Error during test: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    finally:
        # Step 7: Clean up
        logger.info(f"Cleaning up sandbox {session_id}...")
        if session_id in active_sandboxes:
            interpreter = active_sandboxes[session_id]
            try:
                await interpreter.close()
                logger.info(f"Sandbox {session_id} closed successfully")
            except Exception as e:
                logger.error(f"Error closing sandbox: {str(e)}")
            
            # Remove from active sandboxes
            del active_sandboxes[session_id]


# Run the test
if __name__ == "__main__":
    result = asyncio.run(test_chart_tools())
    logger.info("\nTest completed!")
    
    # Check results
    if "error" in result:
        logger.error(f"Test failed: {result['error']}")
        sys.exit(1)
    else:
        logger.info("All charts generated successfully!")