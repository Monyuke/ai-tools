import streamlit as st
from ai_tools.lib.llm import simple_ask
from textwrap import dedent
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama


class Response(BaseModel):
    title: str = Field(default="no_title", description="タイトル")


def st_agent_title(text: str):
    with st.status("タイトル生成中...", expanded=False) as status:
        llm = ChatOllama(model="gpt-oss:20b", reasoning="low").with_structured_output(
            schema=Response
        )
        result = llm.invoke(
            dedent(
                f"""\
                この質問・回答の内容を直接的に反映したわかりやすいタイトルを考えて。

                やりとり：
                {text}
                """
            )
        )
        st.write(str(result))
        title = result.title
        status.update(label="完了", state="complete", expanded=False)
    return title
