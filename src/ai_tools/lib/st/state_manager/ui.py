# src/ai_tools/lib/st/state_manager/ui.py
from __future__ import annotations

import json
from typing import TypeVar

import streamlit as st
from pydantic import BaseModel

from . import StateManager

T = TypeVar("T", bound=BaseModel)


def state_manager_ui(state_manager: StateManager[T]) -> None:
    """
    `state_manager` を受け取り、ロード・ダウンロードボタンを表示する。

    Parameters
    ----------
    state_manager : StateManager[T]
        事前に作成済みの StateManager インスタンス

    Returns
    -------
    None
    """
    # ------------------------------------------------------------------
    # 1. UI のレイアウト
    # ------------------------------------------------------------------
    col_load, col_download = st.columns([1, 1])

    # ------------------------------------------------------------------
    # 2. ロードボタン
    # ------------------------------------------------------------------
    with col_load:
        st.subheader("ロード")
        uploaded_file = st.file_uploader(
            "state.json をアップロード",
            type=["json"],
            key=f"{state_manager.key}_loader",
        )
        if uploaded_file is not None:
            try:
                # ファイルは bytes なので decode
                json_str = uploaded_file.read().decode("utf-8")
                # デシリアライズして保存
                data = state_manager.deserialize(json_str)
                state_manager.store(data)
                st.success("状態をロードしました")
            except Exception as exc:
                st.exception(exc)

    # ------------------------------------------------------------------
    # 3. ダウンロードボタン
    # ------------------------------------------------------------------
    with col_download:
        st.subheader("ダウンロード")
        current = state_manager.get()
        if current is None:
            st.info("現在保存されている状態がありません")
        else:
            json_str = state_manager.serialize(current)
            st.download_button(
                label="state.json をダウンロード",
                data=json_str,
                file_name="state.json",
                mime="application/json",
                key=f"{state_manager.key}_downloader",
            )