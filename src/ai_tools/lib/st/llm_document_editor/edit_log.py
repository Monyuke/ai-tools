# D:\monyuke-dev\ai-tools\src\ai_tools\lib\st\llm_document_editor\edit_log.py

import streamlit as st
from typing import List, Optional


class EditLog:
    """Streamlit の session_state を使って編集ログを保持するクラス"""

    def __init__(self, max_len: int = 256):
        # session_state に初期値を設定
        if "edit_log_max_len" not in st.session_state:
            st.session_state.edit_log_max_len = max_len
        if "edit_log_logs" not in st.session_state:
            st.session_state.edit_log_logs = []  # 直近から順に格納
        if "edit_log_pos" not in st.session_state:
            st.session_state.edit_log_pos = 0  # 0 が最新

    @property
    def max_len(self) -> int:
        return st.session_state.edit_log_max_len

    @property
    def _logs(self) -> List[str]:
        return st.session_state.edit_log_logs

    @property
    def _pos(self) -> int:
        return st.session_state.edit_log_pos

    @_pos.setter
    def _pos(self, value: int) -> None:
        st.session_state.edit_log_pos = value

    def add(self, text: str) -> None:
        """新しいログを追加。最大件数を超えると古いものを削除"""
        self._logs.insert(0, text)
        if len(self._logs) > self.max_len:
            self._logs.pop()
        self._pos = 0

    def prev(self) -> Optional[str]:
        """前のログへ移動。存在しない場合は None"""
        if self._pos + 1 < len(self._logs):
            self._pos += 1
            return self._logs[self._pos]
        return None

    def next(self) -> Optional[str]:
        """次のログへ移動。存在しない場合は None"""
        if self._pos > 0:
            self._pos -= 1
            return self._logs[self._pos]
        return None

    def current(self) -> str:
        """現在のログ（最新）"""
        return self._logs[0] if self._logs else ""

    @staticmethod
    def initialize_session_state(max_len: int = 256) -> None:
        """session_state の初期化を行うヘルパー"""
        st.session_state.setdefault("edit_log_max_len", max_len)
        st.session_state.setdefault("edit_log_logs", [])
        st.session_state.setdefault("edit_log_pos", 0)
