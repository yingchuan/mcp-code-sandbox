# src/tools/chart_tools.py
"""
Chart generation module for the MCP Code Sandbox.
Contains functionality for creating and managing data visualizations.
"""
import logging
import traceback
import base64
import uuid
import os
from typing import Dict, Any, List, Optional

# logger
logger = logging.getLogger('sandbox-server')

class ChartTools:
    """Chart generation operations"""
    
    def __init__(self, active_sandboxes):
        """
        Initialize with a reference to the active sandboxes dictionary
        
        Args:
            active_sandboxes: Dictionary to store active sandbox instances
        """
        self.active_sandboxes = active_sandboxes
    
    def register_tools(self, mcp):
        """Register all graph generation tools with the MCP server"""
        
        @mcp.tool()
        async def generate_line_chart(
            session_id: str, 
            data: List[Dict[str, Any]], 
            x_key: str, 
            y_keys: List[str], 
            title: str = "Line Chart",
            x_label: Optional[str] = None,
            y_label: Optional[str] = None,
            save_path: Optional[str] = None
        ) -> Dict[str, Any]:
            """Generate a line chart from data.
            
            Args:
                session_id: The unique identifier for the sandbox session
                data: List of data points (dictionaries) to plot
                x_key: The key for x-axis values in the data
                y_keys: List of keys for y-axis values to plot as multiple lines
                title: Chart title
                x_label: Label for x-axis (optional)
                y_label: Label for y-axis (optional)
                save_path: File path to save the chart (optional)
            
            Returns:
                A dictionary containing the chart information or an error message
            """
            # Check if sandbox exists
            if session_id not in self.active_sandboxes:
                return {"error": f"No sandbox found with session ID: {session_id}. Create a sandbox first."}
            
            # Get the interpreter
            interpreter = self.active_sandboxes[session_id]
            
            # Default path if none provided
            if not save_path:
                save_path = f"/tmp/line_chart_{uuid.uuid4()}.png"
            
            try:
                # Generate matplotlib code to create the chart
                code = self._generate_line_chart_code(data, x_key, y_keys, title, x_label, y_label, save_path)
                
                # Execute the code
                execution_result = interpreter.run_code(code)
                
                if execution_result.error:
                    logger.error(f"Error generating line chart: {execution_result.error}")
                    return {"error": f"Error generating chart: {execution_result.error}"}
                
                # Check if the file was created
                files_result = interpreter.files.list(os.path.dirname(save_path))
                if os.path.basename(save_path) not in [f["name"] for f in files_result]:
                    return {"error": "Chart file was not created"}
                
                # Read the file as base64
                img_data = interpreter.files.read_bytes(save_path)
                base64_data = base64.b64encode(img_data).decode('utf-8')
                
                return {
                    "chart_type": "line",
                    "title": title,
                    "file_path": save_path,
                    "base64_image": base64_data,
                    "message": "Line chart generated successfully"
                }
            except Exception as e:
                logger.error(f"Error generating line chart in sandbox {session_id}: {str(e)}")
                logger.error(traceback.format_exc())
                return {"error": f"Error generating line chart: {str(e)}"}

        @mcp.tool()
        async def generate_bar_chart(
            session_id: str, 
            data: List[Dict[str, Any]], 
            category_key: str, 
            value_keys: List[str], 
            title: str = "Bar Chart",
            x_label: Optional[str] = None,
            y_label: Optional[str] = None,
            save_path: Optional[str] = None,
            orientation: str = "vertical"
        ) -> Dict[str, Any]:
            """Generate a bar chart from data.
            
            Args:
                session_id: The unique identifier for the sandbox session
                data: List of data points (dictionaries) to plot
                category_key: The key for category labels in the data
                value_keys: List of keys for values to plot as grouped bars
                title: Chart title
                x_label: Label for x-axis (optional)
                y_label: Label for y-axis (optional)
                save_path: File path to save the chart (optional)
                orientation: Bar orientation: "vertical" or "horizontal" (default: "vertical")
            
            Returns:
                A dictionary containing the chart information or an error message
            """
            # Check if sandbox exists
            if session_id not in self.active_sandboxes:
                return {"error": f"No sandbox found with session ID: {session_id}. Create a sandbox first."}
            
            # Get the interpreter
            interpreter = self.active_sandboxes[session_id]
            
            # Default path if none provided
            if not save_path:
                save_path = f"/tmp/bar_chart_{uuid.uuid4()}.png"
            
            try:
                # Generate matplotlib code to create the chart
                code = self._generate_bar_chart_code(
                    data, category_key, value_keys, title, 
                    x_label, y_label, save_path, orientation
                )
                
                # Execute the code
                execution_result = interpreter.run_code(code)
                
                if execution_result.error:
                    logger.error(f"Error generating bar chart: {execution_result.error}")
                    return {"error": f"Error generating chart: {execution_result.error}"}
                
                # Read the file as base64
                img_data = interpreter.files.read_bytes(save_path)
                base64_data = base64.b64encode(img_data).decode('utf-8')
                
                return {
                    "chart_type": "bar",
                    "title": title,
                    "file_path": save_path,
                    "base64_image": base64_data,
                    "message": "Bar chart generated successfully"
                }
            except Exception as e:
                logger.error(f"Error generating bar chart in sandbox {session_id}: {str(e)}")
                return {"error": f"Error generating bar chart: {str(e)}"}

        @mcp.tool()
        async def generate_scatter_plot(
            session_id: str, 
            data: List[Dict[str, Any]], 
            x_key: str, 
            y_key: str,
            color_key: Optional[str] = None,
            size_key: Optional[str] = None,
            title: str = "Scatter Plot",
            x_label: Optional[str] = None,
            y_label: Optional[str] = None,
            save_path: Optional[str] = None
        ) -> Dict[str, Any]:
            """Generate a scatter plot from data.
            
            Args:
                session_id: The unique identifier for the sandbox session
                data: List of data points (dictionaries) to plot
                x_key: The key for x-axis values in the data
                y_key: The key for y-axis values in the data
                color_key: Optional key to use for point colors
                size_key: Optional key to use for point sizes
                title: Chart title
                x_label: Label for x-axis (optional)
                y_label: Label for y-axis (optional)
                save_path: File path to save the chart (optional)
            
            Returns:
                A dictionary containing the chart information or an error message
            """
            # Check if sandbox exists
            if session_id not in self.active_sandboxes:
                return {"error": f"No sandbox found with session ID: {session_id}. Create a sandbox first."}
            
            # Get the interpreter
            interpreter = self.active_sandboxes[session_id]
            
            # Default path if none provided
            if not save_path:
                save_path = f"/tmp/scatter_plot_{uuid.uuid4()}.png"
            
            try:
                # Generate matplotlib code to create the chart
                code = self._generate_scatter_plot_code(
                    data, x_key, y_key, color_key, size_key,
                    title, x_label, y_label, save_path
                )
                
                # Execute the code
                execution_result = interpreter.run_code(code)
                
                if execution_result.error:
                    logger.error(f"Error generating scatter plot: {execution_result.error}")
                    return {"error": f"Error generating chart: {execution_result.error}"}
                
                # Read the file as base64
                img_data = interpreter.files.read_bytes(save_path)
                base64_data = base64.b64encode(img_data).decode('utf-8')
                
                return {
                    "chart_type": "scatter",
                    "title": title,
                    "file_path": save_path,
                    "base64_image": base64_data,
                    "message": "Scatter plot generated successfully"
                }
            except Exception as e:
                logger.error(f"Error generating scatter plot in sandbox {session_id}: {str(e)}")
                return {"error": f"Error generating scatter plot: {str(e)}"}

        @mcp.tool()
        async def generate_interactive_chart(
            session_id: str, 
            chart_type: str,
            data: List[Dict[str, Any]],
            x_key: str,
            y_keys: List[str],
            title: str = "Interactive Chart",
            save_path: Optional[str] = None
        ) -> Dict[str, Any]:
            """Generate an interactive chart using Plotly and return it as HTML.
            
            Args:
                session_id: The unique identifier for the sandbox session
                chart_type: Type of chart to generate: "line", "bar", "scatter", etc.
                data: List of data points (dictionaries) to plot
                x_key: The key for x-axis values in the data
                y_keys: List of keys for y-axis values to plot
                title: Chart title
                save_path: Path to save the HTML file (optional)
            
            Returns:
                A dictionary containing the chart HTML or an error message
            """
            # Check if sandbox exists
            if session_id not in self.active_sandboxes:
                return {"error": f"No sandbox found with session ID: {session_id}. Create a sandbox first."}
            
            # Get the interpreter
            interpreter = self.active_sandboxes[session_id]
            
            # Default path if none provided
            if not save_path:
                save_path = f"/tmp/interactive_chart_{uuid.uuid4()}.html"
            
            try:
                # First check if plotly is installed
                check_result = interpreter.run_code("import sys; 'plotly' in sys.modules")
                
                # If plotly is not installed, install it
                if "ImportError" in check_result.logs or "ModuleNotFoundError" in check_result.logs:
                    logger.info(f"Installing plotly in sandbox {session_id}")
                    install_result = interpreter.run_command("pip install plotly")
                    if install_result.error:
                        return {"error": f"Error installing plotly: {install_result.error}"}
                
                # Generate plotly code
                code = self._generate_plotly_chart_code(
                    chart_type, data, x_key, y_keys, title, save_path
                )
                
                # Execute the code
                execution_result = interpreter.run_code(code)
                
                if execution_result.error:
                    logger.error(f"Error generating interactive chart: {execution_result.error}")
                    return {"error": f"Error generating chart: {execution_result.error}"}
                
                # Read the HTML file
                html_content = interpreter.files.read(save_path)
                
                return {
                    "chart_type": chart_type,
                    "interactive": True,
                    "title": title,
                    "file_path": save_path,
                    "html_content": html_content,
                    "message": "Interactive chart generated successfully"
                }
            except Exception as e:
                logger.error(f"Error generating interactive chart in sandbox {session_id}: {str(e)}")
                return {"error": f"Error generating interactive chart: {str(e)}"}

        @mcp.tool()
        async def generate_heatmap(
            session_id: str,
            data: List[List[float]],
            row_labels: List[str] = None,
            col_labels: List[str] = None,
            title: str = "Heatmap",
            save_path: Optional[str] = None,
            cmap: str = "viridis"
        ) -> Dict[str, Any]:
            """Generate a heatmap visualization.
            
            Args:
                session_id: The unique identifier for the sandbox session
                data: 2D list of values to display in the heatmap
                row_labels: Optional list of row labels
                col_labels: Optional list of column labels
                title: Chart title
                save_path: File path to save the chart (optional)
                cmap: Colormap name (default: "viridis")
            
            Returns:
                A dictionary containing the chart information or an error message
            """
            # Check if sandbox exists
            if session_id not in self.active_sandboxes:
                return {"error": f"No sandbox found with session ID: {session_id}. Create a sandbox first."}
            
            # Get the interpreter
            interpreter = self.active_sandboxes[session_id]
            
            # Default path if none provided
            if not save_path:
                save_path = f"/tmp/heatmap_{uuid.uuid4()}.png"
            
            try:
                # Generate matplotlib code for the heatmap
                code = self._generate_heatmap_code(
                    data, row_labels, col_labels, title, save_path, cmap
                )
                
                # Execute the code
                execution_result = interpreter.run_code(code)
                
                if execution_result.error:
                    logger.error(f"Error generating heatmap: {execution_result.error}")
                    return {"error": f"Error generating heatmap: {execution_result.error}"}
                
                # Read the file as base64
                img_data = interpreter.files.read_bytes(save_path)
                base64_data = base64.b64encode(img_data).decode('utf-8')
                
                return {
                    "chart_type": "heatmap",
                    "title": title,
                    "file_path": save_path,
                    "base64_image": base64_data,
                    "message": "Heatmap generated successfully"
                }
            except Exception as e:
                logger.error(f"Error generating heatmap in sandbox {session_id}: {str(e)}")
                return {"error": f"Error generating heatmap: {str(e)}"}

        # Helper methods for generating code for different chart types
        def _generate_line_chart_code(self, data, x_key, y_keys, title, x_label, y_label, save_path):
            """Generate matplotlib code for a line chart"""
            code = """
import matplotlib.pyplot as plt
import json

# Data preparation
data = {data}
            
# Create figure and axis
plt.figure(figsize=(10, 6), dpi=100)

# Plot each line
for y_key in {y_keys}:
    x_values = [item['{x_key}'] for item in data]
    y_values = [item[y_key] for item in data]
    plt.plot(x_values, y_values, marker='o', linestyle='-', label=y_key)

# Set chart properties
plt.title('{title}', fontsize=16)
plt.xlabel('{x_label}', fontsize=12)
plt.ylabel('{y_label}', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Rotate x-axis labels if there are many
if len(data) > 10:
    plt.xticks(rotation=45)

# Adjust layout
plt.tight_layout()

# Save the chart
plt.savefig('{save_path}')
print(f"Chart saved to {save_path}")
            """.format(
                data=data,
                x_key=x_key,
                y_keys=y_keys,
                title=title,
                x_label=x_label or x_key,
                y_label=y_label or "Value",
                save_path=save_path
            )
            return code

        def _generate_bar_chart_code(self, data, category_key, value_keys, title, x_label, y_label, save_path, orientation):
            """Generate matplotlib code for a bar chart"""
            code = """
import matplotlib.pyplot as plt
import numpy as np
import json

# Data preparation
data = {data}
categories = [item['{category_key}'] for item in data]
value_keys = {value_keys}

# Set up figure and axis
plt.figure(figsize=(12, 7), dpi=100)

# Width of a bar 
bar_width = 0.8 / len(value_keys)
            
# Position of bars on x-axis
indices = np.arange(len(categories))

# Plot bars
for i, value_key in enumerate(value_keys):
    values = [item[value_key] for item in data]
    
    # Adjust position for grouped bars
    position = indices - 0.4 + bar_width * (i + 0.5)
    
    if '{orientation}' == 'horizontal':
        plt.barh(position, values, height=bar_width, label=value_key)
    else:
        plt.bar(position, values, width=bar_width, label=value_key)

# Add labels, title and axes ticks
plt.title('{title}', fontsize=16)

if '{orientation}' == 'horizontal':
    plt.xlabel('{y_label}')
    plt.ylabel('{x_label}')
    plt.yticks(indices, categories)
    if len(categories) > 10:
        plt.yticks(fontsize=8)
else:
    plt.xlabel('{x_label}')
    plt.ylabel('{y_label}')
    plt.xticks(indices, categories)
    if len(categories) > 10:
        plt.xticks(rotation=45, fontsize=8)

plt.grid(True, linestyle='--', alpha=0.3, axis='y')
plt.legend()
plt.tight_layout()

# Save the figure
plt.savefig('{save_path}')
print(f"Chart saved to {save_path}")
            """.format(
                data=data,
                category_key=category_key,
                value_keys=value_keys,
                title=title,
                x_label=x_label or category_key,
                y_label=y_label or "Value",
                save_path=save_path,
                orientation=orientation
            )
            return code

        def _generate_scatter_plot_code(self, data, x_key, y_key, color_key, size_key, title, x_label, y_label, save_path):
            """Generate matplotlib code for a scatter plot"""
            code = """
import matplotlib.pyplot as plt
import numpy as np
import json

# Data preparation
data = {data}
x_values = [item['{x_key}'] for item in data]
y_values = [item['{y_key}'] for item in data]

# Create figure
plt.figure(figsize=(10, 6), dpi=100)

# Define colors and sizes if provided
if {has_color_key}:
    colors = [item['{color_key}'] for item in data]
    # Convert any non-numeric colors to a color map
    if not all(isinstance(c, (int, float)) for c in colors):
        unique_colors = list(set(colors))
        color_map = {{c: i for i, c in enumerate(unique_colors)}}
        colors = [color_map[c] for c in colors]
else:
    colors = 'blue'

if {has_size_key}:
    sizes = [item['{size_key}'] * 20 for item in data]  # Scale sizes
else:
    sizes = 50

# Create the scatter plot
plt.scatter(x_values, y_values, c=colors, s=sizes, alpha=0.7, edgecolors='w')

# Add a color bar if using color mapping
if {has_color_key} and not isinstance(colors, str):
    plt.colorbar(label='{color_key}')

# Set chart properties
plt.title('{title}', fontsize=16)
plt.xlabel('{x_label}', fontsize=12)
plt.ylabel('{y_label}', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.3)

# Tight layout
plt.tight_layout()

# Save the figure
plt.savefig('{save_path}')
print(f"Chart saved to {save_path}")
            """.format(
                data=data,
                x_key=x_key,
                y_key=y_key,
                color_key=color_key or "",
                size_key=size_key or "",
                has_color_key="True" if color_key else "False",
                has_size_key="True" if size_key else "False",
                title=title,
                x_label=x_label or x_key,
                y_label=y_label or y_key,
                save_path=save_path
            )
            return code

        def _generate_plotly_chart_code(self, chart_type, data, x_key, y_keys, title, save_path):
            """Generate Plotly code for an interactive chart"""
            code = """
import plotly.graph_objects as go
import json
from plotly.subplots import make_subplots

# Data preparation
data = {data}
x_values = [item['{x_key}'] for item in data]
chart_type = '{chart_type}'

# Create figure
fig = make_subplots()

# Add traces based on chart type
for y_key in {y_keys}:
    y_values = [item[y_key] for item in data]
    
    if chart_type == 'line':
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name=y_key
        ))
    elif chart_type == 'bar':
        fig.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            name=y_key
        ))
    elif chart_type == 'scatter':
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='markers',
            name=y_key,
            marker=dict(size=10)
        ))
    elif chart_type == 'area':
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines',
            fill='tozeroy',
            name=y_key
        ))
    else:
        # Default to line chart
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name=y_key
        ))

# Update layout
fig.update_layout(
    title='{title}',
    xaxis_title='{x_key}',
    yaxis_title='Value',
    hovermode='closest',
    template='plotly_white'
)

# Add range slider
fig.update_layout(
    xaxis=dict(
        rangeslider=dict(visible=True),
        type='linear'
    )
)

# Write to HTML file
fig.write_html('{save_path}')
print(f"Interactive chart saved to {save_path}")
            """.format(
                data=data,
                x_key=x_key,
                y_keys=y_keys,
                chart_type=chart_type,
                title=title,
                save_path=save_path
            )
            return code

        def _generate_heatmap_code(self, data, row_labels, col_labels, title, save_path, cmap):
            """Generate matplotlib code for a heatmap"""
            code = """
import matplotlib.pyplot as plt
import numpy as np
import json

# Data preparation
data = {data}
data_array = np.array(data)

# Labels
row_labels = {row_labels}
col_labels = {col_labels}

if row_labels is None:
    row_labels = [f'Row {{i}}' for i in range(len(data))]
    
if col_labels is None:
    col_labels = [f'Col {{i}}' for i in range(len(data[0]))]

# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 8), dpi=100)

# Create heatmap
im = ax.imshow(data_array, cmap='{cmap}')

# Add colorbar
cbar = ax.figure.colorbar(im, ax=ax)

# Show all ticks and label them
ax.set_xticks(np.arange(len(col_labels)))
ax.set_yticks(np.arange(len(row_labels)))
ax.set_xticklabels(col_labels)
ax.set_yticklabels(row_labels)

# Rotate the tick labels and set their alignment
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

# Loop over data dimensions and create text annotations
for i in range(len(row_labels)):
    for j in range(len(col_labels)):
        # Choose text color based on background darkness
        color = "white" if data_array[i, j] > data_array.max() / 2 else "black"
        text = ax.text(j, i, f"{{data_array[i, j]:.2f}}",
                       ha="center", va="center", color=color)

# Add title
ax.set_title('{title}')

# Create a tight layout
fig.tight_layout()

# Save the figure
plt.savefig('{save_path}')
print(f"Heatmap saved to {save_path}")
            """.format(
                data=data,
                row_labels=row_labels,
                col_labels=col_labels,
                title=title,
                save_path=save_path,
                cmap=cmap
            )
            return code

        # Make functions available as class methods
        self.generate_line_chart = generate_line_chart
        self.generate_bar_chart = generate_bar_chart
        self.generate_scatter_plot = generate_scatter_plot
        self.generate_interactive_chart = generate_interactive_chart
        self.generate_heatmap = generate_heatmap
        
        return {
            "generate_line_chart": generate_line_chart,
            "generate_bar_chart": generate_bar_chart,
            "generate_scatter_plot": generate_scatter_plot,
            "generate_interactive_chart": generate_interactive_chart,
            "generate_heatmap": generate_heatmap
        }