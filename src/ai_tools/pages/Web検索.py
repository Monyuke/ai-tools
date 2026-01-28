import streamlit as st
from textwrap import dedent
from dataclasses import dataclass, field
from typing import List
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from ai_tools.tools.web_search import web_search, find_in_page, fetch_webpage
from pprint import pprint
from ai_tools.lib.llm import simple_ask
from ai_tools.st_agents.web_search import st_agent_websearch
from ai_tools.st_agents.title import st_agent_title


@dataclass
class AppState:
    # counter: int = 0
    # messages: List[str] = field(default_factory=list)
    ai_message: str = ""
    ai_title: str = ""


if "state" not in st.session_state:
    st.session_state.state = AppState()

st.title("Web検索")

with st.form("search_form"):
    user_text = st.text_area("検索内容", value="")
    submitted = st.form_submit_button("検索")

if submitted:
    st.session_state.state.ai_message = st_agent_websearch(user_text)
    st.session_state.state.ai_title = st_agent_title(
        dedent(
            f"""\
            ユーザー：
            {user_text}
            AI：
            {st.session_state.state.ai_message}
            """
        )
    )

st.markdown(st.session_state.state.ai_message)
st.download_button(
    "Download",
    data=st.session_state.state.ai_message,
    file_name=st.session_state.state.ai_title + ".md",
    mime="text/plain",
)
