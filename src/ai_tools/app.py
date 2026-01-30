import streamlit as st
from textwrap import dedent
from dataclasses import dataclass
from ai_tools.st_agents.web_search import st_agent_websearch
from ai_tools.st_agents.title import st_agent_title
from ai_tools.lib.llm import simple_ask

@dataclass
class AppState:
    # counter: int = 0
    # messages: List[str] = field(default_factory=list)
    ai_message: str = ""


if "state" not in st.session_state:
    st.session_state.state = AppState()

st.title("ASK")

with st.form("ask_form"):
    user_text = st.text_area("内容", value="")
    submitted = st.form_submit_button("実行")

if submitted:
    result = simple_ask(model="gpt-oss:20b",message=user_text)
    st.session_state.state.ai_message = result

st.markdown(st.session_state.state.ai_message)
st.code(st.session_state.state.ai_message, "markdown")
st.download_button(
    "Download",
    data=st.session_state.state.ai_message,
    file_name="ai_result.md",
    mime="text/plain",
)
