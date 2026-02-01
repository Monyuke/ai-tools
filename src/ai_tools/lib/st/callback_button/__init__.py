# ai_tools/lib/st/callback_button/__init__.py
from typing import Any, Callable
import streamlit as st


def callback_button(label: str, callback: Callable[[], Any], **kwargs) -> None:
    """
    Streamlit ボタンを押したときに同期的に callback() を呼び出すラッパー。

    Parameters
    ----------
    label : str
        ボタンに表示する文字列。
    callback : Callable[[], Any]
        ボタン押下時に呼び出す関数。引数は取らない。
    **kwargs
        st.button に渡す任意のキーワード引数（例: key, help, on_click など）。

    Returns
    -------
    None
    """
    if st.button(label, **kwargs):
        try:
            callback()
        except Exception as exc:
            st.exception(exc)
