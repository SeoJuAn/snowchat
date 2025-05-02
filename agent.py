import streamlit as st
from dataclasses import dataclass
from typing import Annotated, Sequence, Optional

from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

from tools import sql_executor_tool, search_tool

@dataclass
class MessagesState:
    messages: Annotated[Sequence[BaseMessage], add_messages]

memory = MemorySaver()

@dataclass
class ModelConfig:
    model_name: str
    api_key: str
    base_url: Optional[str] = None

model_configurations = {
    "o3-mini": ModelConfig(
        model_name="o3-mini", api_key=st.secrets["OPENAI_API_KEY"]
    ),
    # "Grok 2": ModelConfig(
    #     model_name="grok-2-latest",
    #     api_key=st.secrets["XAI_API_KEY"],
    #     base_url="https://api.x.ai/v1",
    # ),
    # "Qwen 2.5": ModelConfig(
    #     model_name="accounts/fireworks/models/qwen2p5-coder-32b-instruct",
    #     api_key=st.secrets["FIREWORKS_API_KEY"],
    #     base_url="https://api.fireworks.ai/inference/v1",
    # ),
    # "Gemini 2.0 Flash": ModelConfig(
    #     model_name="gemini-2.0-flash",
    #     api_key=st.secrets["GEMINI_API_KEY"],
    #     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    # ),
}

def create_agent(callback_handler: BaseCallbackHandler, model_name: str, context_string: str) -> StateGraph:
    config = model_configurations.get(model_name)
    if not config:
        raise ValueError(f"Unsupported model name: {model_name}")

    if not config.api_key:
        raise ValueError(f"API key for model '{model_name}' is not set. Please check your environment variables or secrets configuration.")
    
    # Create the system message with context from all documents
    sys_msg = SystemMessage(
        content=f"""You're an AI assistant specializing in data analysis with Snowflake SQL. 
When providing responses, strive to exhibit friendliness and adopt a conversational tone, similar to how a friend or tutor would communicate.

Here is the documentation and SQL schema information to help you generate accurate SQL queries:

{context_string}

When generating SQL queries:
1. Use the schema information provided above
2. Write clear, efficient SQL that follows best practices
3. Always explain what your SQL query does
4. Format your SQL code with proper indentation inside ```sql code blocks
5. After generating the SQL, immediately call the 'sql_executor' tool with that SQL.
5. Capture the results and include them verbatim in your final answer.
6. Explain both the SQL and its execution results.
7. Always answer in Korean

You have access to the following tools:
- sql_executor: This tool allows you to execute SQL queries directly against a Snowflake database and get the results.
- Internet_Search: This tool allows you to search the internet for snowflake sql related information when needed.

Your goal is to help the user by writing SQL queries that you can then execute to retrieve data from the Snowflake database.
"""
    )

    tools = [sql_executor_tool, search_tool]

    llm = ChatOpenAI(
        model=config.model_name,
        api_key=config.api_key,
        callbacks=[callback_handler],
        streaming=True,
        base_url=config.base_url,
        default_headers={"HTTP-Referer": "https://snowchat.streamlit.app/", "X-Title": "Snowchat"},
    )

    llm_with_tools = llm.bind_tools(tools)

    def llm_agent(state: MessagesState):
        return {"messages": [llm_with_tools.invoke([sys_msg] + state.messages)]}

    builder = StateGraph(MessagesState)
    builder.add_node("llm_agent", llm_agent)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "llm_agent")
    builder.add_conditional_edges("llm_agent", tools_condition)
    builder.add_edge("tools", "llm_agent")
    builder.add_edge("llm_agent", END)
    
    react_graph = builder.compile(checkpointer=memory)

    return react_graph