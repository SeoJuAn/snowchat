import re
import os
import warnings

import streamlit as st
from snowflake.snowpark.exceptions import SnowparkSQLException
from langchain_core.messages import HumanMessage, SystemMessage
from agent import MessagesState, create_agent

from utils.snow_connect import SnowflakeConnection
from utils.snowchat_ui import StreamlitUICallbackHandler, message_func
from utils.snowddl import Snowddl

warnings.filterwarnings("ignore")
chat_history = []
snow_ddl = Snowddl()

# Read all documentation and SQL files
def read_all_files(folder_path, file_extension):
    """Read all files with the specified extension from the folder"""
    contents = {}
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(file_extension):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    contents[filename] = file.read()
    return contents

# Read documentation and SQL files
docs_content = read_all_files('docs', '.md')
sql_content = read_all_files('sql', '.sql')

# Create a consolidated documentation string for the prompt
def create_context_string():
    context = "DOCUMENTATION FILES:\n"
    for filename, content in docs_content.items():
        context += f"\n### {filename} ###\n{content}\n"
    
    context += "\n\nSQL FILES:\n"
    for filename, content in sql_content.items():
        context += f"\n### {filename} ###\n{content}\n"
    
    return context

context_string = create_context_string()

gradient_text_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700;900&display=swap');

.snowchat-title {
  font-family: 'Poppins', sans-serif;
  font-weight: 900;
  font-size: 4em;
  background: linear-gradient(90deg, #ff6a00, #ee0979);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
  margin: 0;
  padding: 20px 0;
  text-align: center;
}
</style>
<div class="snowchat-title">snowChat</div>
"""

st.markdown(gradient_text_html, unsafe_allow_html=True)

st.caption("Talk your way through data")

model_options = {
    "o3-mini": "o3-mini",
    "Qwen 2.5": "Qwen 2.5",
    "Gemini 2.0 Flash": "Gemini 2.0 Flash",
    "Grok 2": "Grok 2",
}

model = st.radio(
    "Choose your AI Model:",
    options=list(model_options.keys()),
    format_func=lambda x: model_options[x],
    index=0,
    horizontal=True,
)
st.session_state["model"] = model

if "assistant_response_processed" not in st.session_state:
    st.session_state["assistant_response_processed"] = True  # Initialize to True

if "toast_shown" not in st.session_state:
    st.session_state["toast_shown"] = False

if "rate-limit" not in st.session_state:
    st.session_state["rate-limit"] = False

# Show a warning if the model is rate-limited
if st.session_state["rate-limit"]:
    st.toast("Probably rate limited.. Go easy folks", icon="⚠️")
    st.session_state["rate-limit"] = False

INITIAL_MESSAGE = [
    {"role": "user", "content": "Hi!"},
    {
        "role": "assistant",
        "content": "Hey there, I'm Chatty McQueryFace, your SQL-speaking sidekick, ready to chat up Snowflake and fetch answers faster than a snowball fight in summer! ❄️🔍",
    },
]
config = {"configurable": {"thread_id": "42"}}

with open("ui/sidebar.md", "r") as sidebar_file:
    sidebar_content = sidebar_file.read()

with open("ui/styles.md", "r") as styles_file:
    styles_content = styles_file.read()

st.sidebar.markdown(sidebar_content)

# selected_table = st.sidebar.selectbox(
#     "Select a table:", options=list(snow_ddl.ddl_dict.keys())
# )
# st.sidebar.markdown(f"### DDL for {selected_table} table")
# st.sidebar.code(snow_ddl.ddl_dict[selected_table], language="sql")

# Add a reset button
if st.sidebar.button("Reset Chat"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state["messages"] = INITIAL_MESSAGE
    st.session_state["history"] = []

st.write(styles_content, unsafe_allow_html=True)

# Initialize the chat messages history
if "messages" not in st.session_state.keys():
    st.session_state["messages"] = INITIAL_MESSAGE

if "history" not in st.session_state:
    st.session_state["history"] = []

if "model" not in st.session_state:
    st.session_state["model"] = model

# Prompt for user input and save
if prompt := st.chat_input():
    if len(prompt) > 500:
        st.error("Input is too long! Please limit your message to 500 characters.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state["assistant_response_processed"] = False  # Assistant response not yet processed

messages_to_display = st.session_state.messages.copy()

for message in messages_to_display:
    message_func(
        message["content"],
        is_user=(message["role"] == "user"),
        is_df=(message["role"] == "data"),
        model=model,
    )

callback_handler = StreamlitUICallbackHandler(model)

react_graph = create_agent(callback_handler, st.session_state["model"], context_string)

def append_chat_history(question, answer):
    st.session_state["history"].append((question, answer))

def get_sql(text):
    sql_match = re.search(r"```sql\n(.*?)\n```", text, re.DOTALL)
    return sql_match.group(1) if sql_match else None

def append_message(content, role="assistant"):
    """Appends a message to the session state messages."""
    if content.strip():
        st.session_state.messages.append({"role": role, "content": content})

if (
    "messages" in st.session_state
    and st.session_state["messages"][-1]["role"] == "user"
    and not st.session_state["assistant_response_processed"]
):
    user_input_content = st.session_state["messages"][-1]["content"]

    if isinstance(user_input_content, str):
        # Start loading animation
        callback_handler.start_loading_message()

        messages = [HumanMessage(content=user_input_content)]

        state = MessagesState(messages=messages)
        result = react_graph.invoke(state, config=config, debug=True)

        if result["messages"]:
            assistant_message = callback_handler.final_message
            append_message(assistant_message)
            st.session_state["assistant_response_processed"] = True