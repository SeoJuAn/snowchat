# import streamlit as st
# from langchain.tools import Tool
# from langchain_community.tools import DuckDuckGoSearchRun
# from utils.snow_connect import SnowflakeConnection
# from typing import Dict, List, Optional, Any
# from pydantic import BaseModel, Field

# class SQLInput(BaseModel):
#     query: str = Field(description="SQL query to be executed")
#     use_cache: bool = Field(default=True, description="Whether to use cached results if available")

# def sql_executor(query: str, use_cache: bool = True) -> str:
#     """
#     Execute snowflake sql queries with optional caching.
#     """
#     conn = SnowflakeConnection()
#     return conn.execute_query(query, use_cache)

# # Create the SQL executor tool
# sql_executor_tool = Tool(
#     name="sql_executor",
#     func=sql_executor,
#     description="Execute a SQL query against the Snowflake database. The query will be executed directly against the Snowflake database."
# )

# # Add search functionality
# search = DuckDuckGoSearchRun()
# search_tool = Tool(
#     name="Internet_Search",
#     func=search.run,
#     description="Search the internet for snowflake sql related information when needed to generate SQL code."
# )


#=============================Pyecharts 추가 버전=============================
import streamlit as st
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from utils.snow_connect import SnowflakeConnection
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import json
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie, Scatter
from pyecharts.globals import ThemeType

class SQLInput(BaseModel):
    query: str = Field(description="SQL query to be executed")
    use_cache: bool = Field(default=True, description="Whether to use cached results if available")

class VisualizationInput(BaseModel):
    data: str = Field(description="JSON string representation of the data to visualize")
    chart_type: str = Field(description="Type of chart to create (bar, line, pie, scatter)")
    title: str = Field(description="Chart title")
    x_field: str = Field(description="Field name to use for X-axis")
    y_field: str = Field(description="Field name to use for Y-axis or values")
    category_field: Optional[str] = Field(None, description="Optional field for categories/grouping")

def sql_executor(query: str, use_cache: bool = True) -> str:
    """
    Execute snowflake sql queries with optional caching.
    """
    conn = SnowflakeConnection()
    return conn.execute_query(query, use_cache)

def create_visualization(data_input: str) -> str:
    """
    Create a visualization using Pyecharts based on the data and parameters provided.
    Returns an HTML string containing the visualization.
    """
    try:
        # Parse the input JSON data
        data_input_json = json.loads(data_input)
        
        # Extract parameters from the input
        data_str = data_input_json.get('data')
        chart_type = data_input_json.get('chart_type')
        title = data_input_json.get('title')
        x_field = data_input_json.get('x_field')
        y_field = data_input_json.get('y_field')
        category_field = data_input_json.get('category_field')
        
        # Verify all required parameters are present
        if not all([data_str, chart_type, title, x_field, y_field]):
            return "Missing required parameters. Please provide data, chart_type, title, x_field, and y_field."
        
        # Parse the data
        if isinstance(data_str, str):
            # If data is provided as a string, parse it
            data_dict = json.loads(data_str)
        else:
            # If data is already parsed (list of dictionaries)
            data_dict = data_str
        
        # Convert to pandas DataFrame for easier manipulation
        df = pd.DataFrame(data_dict)
        
        # Initialize the chart based on the chart_type
        if chart_type.lower() == "bar":
            chart = Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        elif chart_type.lower() == "line":
            chart = Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        elif chart_type.lower() == "pie":
            chart = Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        elif chart_type.lower() == "scatter":
            chart = Scatter(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        else:
            return "Unsupported chart type. Please use 'bar', 'line', 'pie', or 'scatter'."
        
        # Set global options
        chart.set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            tooltip_opts=opts.TooltipOpts(),
            legend_opts=opts.LegendOpts()
        )
        
        # Different chart types require different data processing
        if chart_type.lower() == "pie":
            data_pairs = [(row[x_field], row[y_field]) for _, row in df.iterrows()]
            chart.add(
                series_name="",
                data_pair=data_pairs,
                label_opts=opts.LabelOpts(formatter="{b}: {c}")
            )
        elif chart_type.lower() == "scatter":
            if category_field:
                categories = df[category_field].unique()
                for category in categories:
                    filtered_df = df[df[category_field] == category]
                    chart.add_xaxis(filtered_df[x_field].tolist())
                    chart.add_yaxis(
                        series_name=str(category),
                        y_axis=filtered_df[y_field].tolist(),
                        symbol_size=10,
                        label_opts=opts.LabelOpts(is_show=False)
                    )
            else:
                chart.add_xaxis(df[x_field].tolist())
                chart.add_yaxis(
                    series_name="",
                    y_axis=df[y_field].tolist(),
                    symbol_size=10,
                    label_opts=opts.LabelOpts(is_show=False)
                )
        else:  # Bar and Line charts
            if category_field:
                categories = df[category_field].unique()
                x_values = df[x_field].unique().tolist()
                chart.add_xaxis(x_values)
                
                for category in categories:
                    filtered_df = df[df[category_field] == category]
                    # Create a mapping of x_field to y_field
                    y_values = []
                    for x in x_values:
                        matched_rows = filtered_df[filtered_df[x_field] == x]
                        y_value = matched_rows[y_field].sum() if not matched_rows.empty else 0
                        y_values.append(y_value)
                    
                    chart.add_yaxis(
                        series_name=str(category),
                        y_axis=y_values,
                        label_opts=opts.LabelOpts(is_show=False)
                    )
            else:
                chart.add_xaxis(df[x_field].tolist())
                chart.add_yaxis(
                    series_name="",
                    y_axis=df[y_field].tolist(),
                    label_opts=opts.LabelOpts(is_show=False)
                )
        
        # Render the chart to HTML
        html = chart.render_embed()
        return f"<visualization>{html}</visualization>"
    
    except Exception as e:
        return f"Error creating visualization: {str(e)}"


# Create the SQL executor tool
sql_executor_tool = Tool(
    name="sql_executor",
    func=sql_executor,
    description="Execute a SQL query against the Snowflake database. The query will be executed directly against the Snowflake database."
)

# Create the visualization tool
visualization_tool = Tool(
    name="data_visualization",
    func=create_visualization,
    description="Create a visualization chart from data. Requires data in JSON format, chart type (bar, line, pie, scatter), title, x-field, y-field, and optional category field for grouping."
)

# Add search functionality
search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="Internet_Search",
    func=search.run,
    description="Search the internet for snowflake sql related information when needed to generate SQL code."
)