import streamlit as st
from typing import Callable
from ai_tools.tools.edit.edit_data import EditData, EditType


def edit_item(
    edit: EditData,
    on_apply: Callable[[EditData], None],
    key_prefix: str = "",
) -> None:
    """
    1 つの EditData を表示・編集・適用するコンポーネント

    Parameters
    ----------
    edit : EditData
        編集対象
    on_apply : Callable[[EditData], None]
        適用ボタン押下時に呼ばれるコールバック
    key_prefix : str
        Streamlit の key を一意にするためのプレフィックス
    """
    # 1 行ずつ表示
    with st.expander(f"{edit.file} ({edit.type.value})", expanded=False):
        # ファイル名は編集不可
        st.text(f"File: {edit.file}")

        # search, replace はテキスト入力
        new_search = st.text_area(
            "Search", value=edit.search, key=f"{key_prefix}_search", height=200
        )
        new_replace = st.text_area(
            "Replace", value=edit.replace, key=f"{key_prefix}_replace", height=400
        )

        # type は選択肢
        new_type = st.selectbox(
            "Type",
            options=[t.value for t in EditType],
            index=[t.value for t in EditType].index(edit.type.value),
            key=f"{key_prefix}_type",
        )

        # 適用ボタン
        if st.button("Apply", key=f"{key_prefix}_apply"):
            # 変更を EditData に反映
            edit.search = new_search
            edit.replace = new_replace
            edit.type = EditType(new_type)
            on_apply(edit)
