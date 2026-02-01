import streamlit as st
from typing import List
from ai_tools.tools.edit.edit_data import EditData
from .edit_item import edit_item

def edit_list(edits: List[EditData]) -> None:
    """
    EditData のリストを表示し、個別に編集・適用できる UI

    Parameters
    ----------
    edits : List[EditData]
        編集対象リスト
    """
    # 変更状態を保持するために session_state を使う
    if "applied" not in st.session_state:
        st.session_state.applied = {id(e): False for e in edits}

    def apply_callback(edit: EditData):
        # 実際にファイルに適用するロジックは別モジュールに委譲
        from ai_tools.tools.edit.utils import edit_one
        edit_one(edit)
        st.session_state.applied[id(edit)] = True
        st.success(f"Applied: {edit.file}")

    for idx, edit in enumerate(edits):
        key = f"edit_{idx}"
        if st.session_state.applied.get(id(edit), False):
            st.markdown(f"✅ **Applied**: {edit.file}")
        else:
            edit_item(edit, apply_callback, key_prefix=key)