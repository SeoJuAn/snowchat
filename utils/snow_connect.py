# from typing import Any, Dict
# import json
# import requests
# import streamlit as st
# from snowflake.snowpark.session import Session


# class SnowflakeConnection:
#     """
#     This class is used to establish a connection to Snowflake and execute queries with optional caching.

#     Attributes
#     ----------
#     connection_parameters : Dict[str, Any]
#         A dictionary containing the connection parameters for Snowflake.
#     session : snowflake.snowpark.Session
#         A Snowflake session object.

#     Methods
#     -------
#     get_session()
#         Establishes and returns the Snowflake connection session.
#     execute_query(query: str, use_cache: bool = True)
#         Executes a Snowflake SQL query with optional caching.
#     """

#     def __init__(self):
#         self.connection_parameters = self._get_connection_parameters_from_env()
#         self.session = None
#         self.cloudflare_account_id = st.secrets["CLOUDFLARE_ACCOUNT_ID"]
#         self.cloudflare_namespace_id = st.secrets["CLOUDFLARE_NAMESPACE_ID"]
#         self.cloudflare_api_token = st.secrets["CLOUDFLARE_API_TOKEN"]
#         self.headers = {
#             "Authorization": f"Bearer {self.cloudflare_api_token}",
#             "Content-Type": "application/json"
#         }

#     @staticmethod
#     def _get_connection_parameters_from_env() -> Dict[str, Any]:
#         return {
#             "account": st.secrets["ACCOUNT"],
#             "user": st.secrets["USER_NAME"],
#             "password": st.secrets["PASSWORD"],
#             "warehouse": st.secrets["WAREHOUSE"],
#             "database": st.secrets["DATABASE"],
#             "schema": st.secrets["SCHEMA"],
#             "role": st.secrets["ROLE"],
#         }

#     def get_session(self):
#         """
#         Establishes and returns the Snowflake connection session.
#         Returns:
#             session: Snowflake connection session.
#         """
#         if self.session is None:
#             self.session = Session.builder.configs(self.connection_parameters).create()
#             self.session.sql_simplifier_enabled = True
#         return self.session

#     def _construct_kv_url(self, key: str) -> str:
#         return f"https://api.cloudflare.com/client/v4/accounts/{self.cloudflare_account_id}/storage/kv/namespaces/{self.cloudflare_namespace_id}/values/{key}"

#     def get_from_cache(self, key: str) -> str:
#         url = self._construct_kv_url(key)
#         try:
#             response = requests.get(url, headers=self.headers)
#             response.raise_for_status()
#             print("\n\n\nCache hit\n\n\n")
#             return response.text
#         except requests.exceptions.RequestException as e:
#             print(f"Cache miss or error: {e}")
#         return None

#     def set_to_cache(self, key: str, value: str) -> None:
#         url = self._construct_kv_url(key)
#         serialized_value = json.dumps(value)
#         try:
#             response = requests.put(url, headers=self.headers, data=serialized_value)
#             response.raise_for_status()
#             print("Cache set successfully")
#         except requests.exceptions.RequestException as e:
#             print(f"Failed to set cache: {e}")

#     def execute_query(self, query: str, use_cache: bool = True) -> str:
#         """
#         Execute a Snowflake SQL query with optional caching.
#         """
#         if use_cache:
#             cached_response = self.get_from_cache(query)
#             if cached_response:
#                 return json.loads(cached_response)

#         session = self.get_session()
#         result = session.sql(query).collect()
#         result_list = [row.as_dict() for row in result]

#         if use_cache:
#             self.set_to_cache(query, result_list)

#         return result_list

















# from typing import Any, Dict
# import streamlit as st
# from snowflake.snowpark.session import Session


# class SnowflakeConnection:
#     """
#     This class is used to establish a connection to Snowflake and execute queries directly (no caching).
#     """

#     def __init__(self):
#         self.connection_parameters = self._get_connection_parameters_from_env()
#         self.session = None

#     @staticmethod
#     def _get_connection_parameters_from_env() -> Dict[str, Any]:
#         return {
#             "account": st.secrets["ACCOUNT"],
#             "user": st.secrets["USER_NAME"],
#             "password": st.secrets["PASSWORD"],
#             "warehouse": st.secrets["WAREHOUSE"],
#             "database": st.secrets["DATABASE"],
#             "schema": st.secrets["SCHEMA"],
#             "role": st.secrets["ROLE"],
#         }

#     def get_session(self):
#         """
#         Establishes and returns the Snowflake connection session.
#         """
#         if self.session is None:
#             self.session = Session.builder.configs(self.connection_parameters).create()
#             self.session.sql_simplifier_enabled = True
#         return self.session

#     def execute_query(self, query: str) -> str:
#         """
#         Execute a Snowflake SQL query without any caching.
#         """
#         session = self.get_session()
#         result = session.sql(query).collect()
#         result_list = [row.as_dict() for row in result]
#         return result_list



from typing import Any, Dict, List
import streamlit as st
from snowflake.snowpark.session import Session
import pandas as pd

class SnowflakeConnection:
    """
    This class is used to establish a connection to Snowflake and execute queries.
    """

    def __init__(self):
        self.connection_parameters = self._get_connection_parameters_from_env()
        self.session = None
        self._cache = {}  # Simple in-memory cache

    @staticmethod
    def _get_connection_parameters_from_env() -> Dict[str, Any]:
        return {
            "account": st.secrets["ACCOUNT"],
            "user": st.secrets["USER_NAME"],
            "password": st.secrets["PASSWORD"],
            "warehouse": st.secrets["WAREHOUSE"],
            "database": st.secrets["DATABASE"],
            "schema": st.secrets["SCHEMA"],
            "role": st.secrets["ROLE"],
        }

    def get_session(self):
        """
        Establishes and returns the Snowflake connection session.
        """
        if self.session is None:
            self.session = Session.builder.configs(self.connection_parameters).create()
            self.session.sql_simplifier_enabled = True
        return self.session

    def execute_query(self, query: str, use_cache: bool = True) -> str:
        """
        Execute a Snowflake SQL query and return results as a formatted string.
        
        Args:
            query (str): The SQL query to execute
            use_cache (bool): Whether to use cached results if available
            
        Returns:
            str: Formatted results of the query or error message
        """
        # Check cache first if caching is enabled
        if use_cache and query in self._cache:
            return self._cache[query]
        
        session = self.get_session()
        try:
            result = session.sql(query).collect()
            result_list = [row.as_dict() for row in result]
            
            if not result_list:
                return "Query executed successfully, but returned no results."
            
            # Format the result as a markdown table for cleaner display
            columns = list(result_list[0].keys())
            
            markdown_table = "| " + " | ".join(columns) + " |\n"
            markdown_table += "| " + " | ".join(["---" for _ in columns]) + " |\n"
            
            for row in result_list:
                markdown_table += "| " + " | ".join([str(row.get(col, '')) for col in columns]) + " |\n"
            
            response = f"SQL query executed successfully. Results:\n\n{markdown_table}"
            
            # Cache result if caching is enabled
            if use_cache:
                self._cache[query] = response
                
            return response
        except Exception as e:
            error_response = f"Error executing SQL query: {str(e)}"
            return error_response
    
    def sql(self, query: str):
        """
        Execute a SQL query and return the result set.
        """
        session = self.get_session()
        return session.sql(query)