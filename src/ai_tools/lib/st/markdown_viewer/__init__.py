# src/ai_tools/lib/st/markdown_viewer/__init__.py
"""
Markdown Viewer for Streamlit.

Provides a simple component that shows a Markdown document in three tabs:
Preview, Code, and optionally Edit.  The Edit tab is only shown when an
`on_change` callback is supplied.
"""

from __future__ import annotations

from typing import Callable, Optional

import streamlit as st


def markdown_viewer(
    body: str,
    on_change: Optional[Callable[[str], None]] = None,
) -> None:
    """
    Render a Markdown viewer with optional edit capability.

    Parameters
    ----------
    body : str
        Markdown content to display.
    on_change : Optional[Callable[[str], None]], default None
        Callback invoked when the user edits the Markdown in the Edit tab.
        The callback receives the updated Markdown string as its sole
        argument.  If ``None``, the Edit tab is omitted.

    Returns
    -------
    None
    """
    # タブのラベルを作成
    tab_labels = ["Preview", "Code"]
    if on_change is not None:
        tab_labels.append("Edit")

    # タブを作成
    tabs = st.tabs(tab_labels)

    # Preview タブ
    with tabs[0]:
        st.markdown(body, unsafe_allow_html=True)

    # Code タブ
    with tabs[1]:
        st.code(body, language="markdown")

    # Edit タブ（存在する場合）
    if on_change is not None:
        # Streamlit のテキストエリアは key が必要
        edit_key = f"markdown_viewer_edit_{id(body)}"

        def _on_change_wrapper() -> None:
            """内部コールバック: 最新のテキストを取得して外部コールバックへ渡す"""
            current_text = st.session_state.get(edit_key, body)
            on_change(current_text)

        with tabs[2]:
            st.text_area(
                label="Edit Markdown",
                value=body,
                key=edit_key,
                on_change=_on_change_wrapper,
            )