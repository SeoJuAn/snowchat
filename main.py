# # ───────────────────────────── main.py (2025-05-06 완전 수정본) ─────────────────────────────
# import os
# import re
# import warnings
# import json

# import streamlit as st
# from langchain_core.messages import HumanMessage
# from agent import MessagesState, create_agent
# from utils.snowchat_ui import StreamlitUICallbackHandler, message_func
# from utils.snowddl import Snowddl

# # ───────────────────────────── 기본 설정 ─────────────────────────────
# warnings.filterwarnings("ignore")
# snow_ddl = Snowddl()

# # ───────────────────── 문서 · SQL 파일 읽기 유틸 ─────────────────────
# def read_all_files(folder_path: str, file_ext: str) -> dict:
#     contents = {}
#     if os.path.exists(folder_path):
#         for filename in os.listdir(folder_path):
#             if filename.endswith(file_ext):
#                 with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
#                     contents[filename] = f.read()
#     return contents

# docs_content = read_all_files("docs", ".md")
# sql_content  = read_all_files("sql",  ".sql")

# def create_context_string() -> str:
#     parts = ["DOCUMENTATION FILES:"]
#     for fname, txt in docs_content.items():
#         parts.append(f"\n### {fname} ###\n{txt}\n")
#     parts.append("\nSQL FILES:")
#     for fname, txt in sql_content.items():
#         parts.append(f"\n### {fname} ###\n{txt}\n")
#     return "\n".join(parts)

# context_string = create_context_string()

# # ───────────────────────────── 타이틀 / 스타일 ─────────────────────────────
# gradient_text_html = """
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700;900&display=swap');
# .snowchat-title {
#   font-family: 'Poppins', sans-serif;
#   font-weight: 900;
#   font-size: 4em;
#   background: linear-gradient(90deg,#ff6a00,#ee0979);
#   -webkit-background-clip:text;
#   -webkit-text-fill-color:transparent;
#   text-shadow:2px 2px 5px rgba(0,0,0,.3);
#   margin:0;padding:20px 0;text-align:center;
# }
# </style>
# <div class="snowchat-title">snowChat</div>
# """
# st.markdown(gradient_text_html, unsafe_allow_html=True)
# st.caption("Talk your way through data")

# # ───────────────────────────── 모델 선택 ─────────────────────────────
# model_options = {
#     "o3-mini": "o3-mini",
#     "Qwen 2.5": "Qwen 2.5",
#     "Gemini 2.0 Flash": "Gemini 2.0 Flash",
#     "Grok 2": "Grok 2",
# }
# model = st.radio(
#     "Choose your AI Model:",
#     options=list(model_options.keys()),
#     format_func=lambda x: model_options[x],
#     index=0,
#     horizontal=True,
# )
# st.session_state["model"] = model

# # ───────────────────────── SessionState 초기화 ─────────────────────────
# if "messages" not in st.session_state:
#     st.session_state["messages"] = []
# if "history" not in st.session_state:
#     st.session_state["history"] = []
# if "assistant_response_processed" not in st.session_state:
#     st.session_state["assistant_response_processed"] = True
# for flag in ("toast_shown", "rate-limit"):
#     if flag not in st.session_state:
#         st.session_state[flag] = False

# # 최초 시스템 메시지 세팅
# INITIAL_MESSAGE = [
#     {"role": "user", "content": "Hi!"},
#     {
#         "role": "assistant",
#         "content": (
#             "안녕하세요! 저는 Chatty McQueryFace입니다. "
#             "SQL을 사용하여 Snowflake 데이터베이스를 탐색하는 데 도움을 드릴 수 있어요. "
#             "데이터 시각화도 할 수 있으니 필요하시면 말씀해주세요! ❄️🔍"
#         ),
#     },
# ]
# if not st.session_state["messages"]:
#     st.session_state["messages"] = INITIAL_MESSAGE

# # ─────────────────────────── 사이드바 ───────────────────────────
# with open("ui/sidebar.md", "r") as f:
#     st.sidebar.markdown(f.read())
# with open("ui/styles.md", "r") as f:
#     st.write(f.read(), unsafe_allow_html=True)

# if st.sidebar.button("Reset Chat"):
#     for k in list(st.session_state.keys()):
#         del st.session_state[k]
#     st.session_state["messages"] = INITIAL_MESSAGE
#     st.session_state["history"]  = []

# # ─────────────────────── 사용자 입력 & 메시지 렌더 ───────────────────────
# if prompt := st.chat_input():
#     if len(prompt) > 500:
#         st.error("Input is too long! Please limit your message to 500 characters.")
#     else:
#         st.session_state["messages"].append({"role": "user", "content": prompt})
#         st.session_state["assistant_response_processed"] = False

# # 메시지·차트 순서대로 출력
# for msg in st.session_state["messages"]:
#     if msg["role"] == "visualization":
#         st.components.v1.html(msg["content"], height=500, scrolling=False)
#     else:
#         message_func(
#             msg["content"],
#             is_user=(msg["role"] == "user"),
#             is_df=(msg["role"] == "data"),
#             model=model,
#         )

# # ───────────────────── Agent 초기화 ─────────────────────
# callback_handler = StreamlitUICallbackHandler(model)
# react_graph = create_agent(callback_handler, model, context_string)

# # ───────────────────── 헬퍼 함수 ─────────────────────
# def append_message(content: str, role: str = "assistant"):
#     if content.strip():
#         st.session_state["messages"].append({"role": role, "content": content})

# def display_visualization(html: str):
#     """차트를 visualization 메시지로 추가하고 즉시 렌더"""
#     st.session_state["messages"].append({"role": "visualization", "content": html})
#     st.components.v1.html(html, height=500, scrolling=False)

# # ───────────────────── LLM / Tool 실행 ─────────────────────
# if (
#     st.session_state["messages"][-1]["role"] == "user"
#     and not st.session_state["assistant_response_processed"]
# ):
#     user_input = st.session_state["messages"][-1]["content"]
#     callback_handler.start_loading_message()

#     state  = MessagesState(messages=[HumanMessage(content=user_input)])
#     result = react_graph.invoke(
#         state,
#         config={"configurable": {"thread_id": "42"}},
#         debug=True,
#     )

#     # ───── visualization 태그 추출 ─────
#     viz_pattern = r"<visualization>(.*?)</visualization>"
#     viz_html = None

#     # 1) ToolMessage 들 먼저 스캔
#     for m in result["messages"]:
#         try:
#             if isinstance(m.content, str):
#                 found = re.search(viz_pattern, m.content, re.DOTALL)
#                 if found:
#                     viz_html = found.group(1)
#                     break
#         except AttributeError:
#             pass

#     # 2) assistant 최종 메시지
#     assistant_msg = callback_handler.final_message
#     if viz_html is None:
#         found = re.search(viz_pattern, assistant_msg, re.DOTALL)
#         if found:
#             viz_html = found.group(1)
#             assistant_msg = re.sub(viz_pattern, "", assistant_msg, flags=re.DOTALL)
#     else:
#         assistant_msg = re.sub(viz_pattern, "", assistant_msg, flags=re.DOTALL)

#     # ───── 결과 표시 ─────
#     append_message(assistant_msg)
#     if viz_html:
#         display_visualization(viz_html)

#     st.session_state["assistant_response_processed"] = True
# # ────────────────────────────────────────────────────────────────────



# ───────────────────────────── main.py (2025-05-06 완전 수정본) ─────────────────────────────
import os
import re
import warnings
import json

import streamlit as st
from langchain_core.messages import HumanMessage
from agent import MessagesState, create_agent
from utils.snowchat_ui import StreamlitUICallbackHandler, message_func
from utils.snowddl import Snowddl

# ───────────────────────────── 기본 설정 ─────────────────────────────
warnings.filterwarnings("ignore")
snow_ddl = Snowddl()

# ───────────────────── 문서 · SQL 파일 읽기 유틸 ─────────────────────
def read_all_files(folder_path: str, file_ext: str) -> dict:
    contents = {}
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(file_ext):
                with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                    contents[filename] = f.read()
    return contents

docs_content = read_all_files("docs", ".md")
sql_content  = read_all_files("sql",  ".sql")

def create_context_string() -> str:
    parts = ["DOCUMENTATION FILES:"]
    for fname, txt in docs_content.items():
        parts.append(f"\n### {fname} ###\n{txt}\n")
    parts.append("\nSQL FILES:")
    for fname, txt in sql_content.items():
        parts.append(f"\n### {fname} ###\n{txt}\n")
    return "\n".join(parts)

context_string = create_context_string()

# ───────────────────────────── 타이틀 / 스타일 ─────────────────────────────
gradient_text_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700;900&display=swap');
.snowchat-title {
  font-family: 'Poppins', sans-serif;
  font-weight: 900;
  font-size: 4em;
  background: linear-gradient(90deg,#ff6a00,#ee0979);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  text-shadow:2px 2px 5px rgba(0,0,0,.3);
  margin:0;padding:20px 0;text-align:center;
}
</style>
<div class="snowchat-title">snowChat</div>
"""
st.markdown(gradient_text_html, unsafe_allow_html=True)
st.caption("Talk your way through data")

# ───────────────────────────── 모델 선택 ─────────────────────────────
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

# ───────────────────────── SessionState 초기화 ─────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "history" not in st.session_state:
    st.session_state["history"] = []
if "assistant_response_processed" not in st.session_state:
    st.session_state["assistant_response_processed"] = True
for flag in ("toast_shown", "rate-limit"):
    if flag not in st.session_state:
        st.session_state[flag] = False

# 최초 시스템 메시지 세팅
INITIAL_MESSAGE = [
    {"role": "user", "content": "Hi!"},
    {
        "role": "assistant",
        "content": (
            "안녕하세요! 저는 Chatty McQueryFace입니다. "
            "SQL을 사용하여 Snowflake 데이터베이스를 탐색하는 데 도움을 드릴 수 있어요. "
            "데이터 시각화도 할 수 있으니 필요하시면 말씀해주세요! ❄️🔍"
        ),
    },
]
if not st.session_state["messages"]:
    st.session_state["messages"] = INITIAL_MESSAGE

# ─────────────────────────── 사이드바 ───────────────────────────
with open("ui/sidebar.md", "r") as f:
    st.sidebar.markdown(f.read())
with open("ui/styles.md", "r") as f:
    st.write(f.read(), unsafe_allow_html=True)

if st.sidebar.button("Reset Chat"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state["messages"] = INITIAL_MESSAGE
    st.session_state["history"]  = []

# ─────────────────────── 사용자 입력 & 메시지 렌더 ───────────────────────
if prompt := st.chat_input():
    if len(prompt) > 500:
        st.error("Input is too long! Please limit your message to 500 characters.")
    else:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        st.session_state["assistant_response_processed"] = False

# 메시지·차트 순서대로 출력
for msg in st.session_state["messages"]:
    if msg["role"] == "visualization":
        st.components.v1.html(msg["content"], height=500, scrolling=False)
    else:
        message_func(
            msg["content"],
            is_user=(msg["role"] == "user"),
            is_df=(msg["role"] == "data"),
            model=model,
        )

# ───────────────────── Agent 초기화 ─────────────────────
callback_handler = StreamlitUICallbackHandler(model)
react_graph = create_agent(callback_handler, model, context_string)

# ───────────────────── 헬퍼 함수 ─────────────────────
def append_message(content: str, role: str = "assistant"):
    if content.strip():
        st.session_state["messages"].append({"role": role, "content": content})

def display_visualization(html: str):
    """차트를 visualization 메시지로 추가하고 즉시 렌더"""
    st.session_state["messages"].append({"role": "visualization", "content": html})
    st.components.v1.html(html, height=500, scrolling=False)

# ───────────────────── LLM / Tool 실행 ─────────────────────
if (
    st.session_state["messages"][-1]["role"] == "user"
    and not st.session_state["assistant_response_processed"]
):
    user_input = st.session_state["messages"][-1]["content"]
    callback_handler.start_loading_message()

    state  = MessagesState(messages=[HumanMessage(content=user_input)])
    result = react_graph.invoke(
        state,
        config={"configurable": {"thread_id": "42"}},
        debug=True,
    )

    viz_pattern = r"<visualization>(.*?)</visualization>"
    viz_html = None

    # ───── 1) assistant 최종 메시지에서 먼저 찾기 ─────
    assistant_msg = callback_handler.final_message
    match = re.search(viz_pattern, assistant_msg, re.DOTALL)
    if match:
        viz_html = match.group(1)
        assistant_msg = re.sub(viz_pattern, "", assistant_msg, flags=re.DOTALL)

    # ───── 2) 없으면 메시지 리스트를 '역순'으로 검색 ★ ─────
    if viz_html is None:
        for m in reversed(result["messages"]):       # ★ 최신부터 확인
            try:
                if isinstance(m.content, str):
                    match = re.search(viz_pattern, m.content, re.DOTALL)
                    if match:
                        viz_html = match.group(1)
                        break                        # ★ 최신 차트 하나만
            except AttributeError:
                pass

    # ───── 결과 표시 ─────
    append_message(assistant_msg)
    if viz_html:
        display_visualization(viz_html)

    st.session_state["assistant_response_processed"] = True
# ────────────────────────────────────────────────────────────────────
