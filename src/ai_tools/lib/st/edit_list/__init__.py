from .edit_list import edit_list
import streamlit as st
from typing import List
from ai_tools.tools.edit.edit_data import EditData
from ai_tools.tools.edit import build_edit_data_list


def edit_list_builder(prompt: str) -> None:
    """
    プロンプトから EditData リストを生成して表示するコンポーネント
    
    Parameters
    ----------
    prompt : str
        編集内容を指示するプロンプト
    """
    if st.button("Build Edit List"):
        with st.spinner("Generating edit list..."):
            edits = build_edit_data_list(
                user_prompt=prompt,
                model="qwen3:14b",
                reasoning="low"
            )
            st.session_state.generated_edits = edits
    
    if "generated_edits" in st.session_state:
        st.divider()
        edit_list(st.session_state.generated_edits)
