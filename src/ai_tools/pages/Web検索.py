import streamlit as st
from textwrap import dedent
from dataclasses import dataclass
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
    result = st_agent_websearch(user_text)
    st.session_state.state.ai_message = result.body
    st.session_state.state.ai_title = result.title

st.markdown(st.session_state.state.ai_message)
st.download_button(
    "Download",
    data=st.session_state.state.ai_message,
    file_name=st.session_state.state.ai_title + ".md",
    mime="text/plain",
)
