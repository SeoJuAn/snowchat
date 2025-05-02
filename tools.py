import streamlit as st
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from utils.snow_connect import SnowflakeConnection
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class SQLInput(BaseModel):
    query: str = Field(description="SQL query to be executed")
    use_cache: bool = Field(default=True, description="Whether to use cached results if available")

def sql_executor(query: str, use_cache: bool = True) -> str:
    """
    Execute snowflake sql queries with optional caching.
    """
    conn = SnowflakeConnection()
    return conn.execute_query(query, use_cache)

# Create the SQL executor tool
sql_executor_tool = Tool(
    name="sql_executor",
    func=sql_executor,
    description="Execute a SQL query against the Snowflake database. The query will be executed directly against the Snowflake database."
)

# Add search functionality
search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="Internet_Search",
    func=search.run,
    description="Search the internet for snowflake sql related information when needed to generate SQL code."
)