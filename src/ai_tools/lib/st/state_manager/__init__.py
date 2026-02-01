# src/ai_tools/lib/st/state_manager/state_manager.py
from __future__ import annotations

import json
from typing import Generic, Optional, Type, TypeVar

import streamlit as st
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class StateManager(Generic[T]):
    """
    Streamlit session_state 用の汎用データ管理クラス。

    Parameters
    ----------
    key : str
        session_state 内で使用するキー
    model_cls : Type[T]
        取り扱うモデルクラス（pydantic.BaseModel を継承したもの）
    """

    def __init__(self, key: str, model_cls: Type[T]) -> None:
        self.key = key
        self.model_cls = model_cls

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def store(self, data: T) -> None:
        """session_state にデータを保存"""
        st.session_state[self.key] = data

    def get(self) -> Optional[T]:
        """session_state からデータを取得。無い場合は None"""
        raw = st.session_state.get(self.key)
        if raw is None:
            return None
        # 既にオブジェクトが入っている場合はそのまま返す
        if isinstance(raw, self.model_cls):
            return raw
        # 文字列や dict から復元
        if isinstance(raw, str):
            return self.deserialize(raw)
        if isinstance(raw, dict):
            return self.model_cls.parse_obj(raw)
        raise TypeError(
            f"Unsupported type stored in session_state[{self.key}]: {type(raw)}"
        )

    def get_or_create(self) -> T:
        existing = self.get()
        if existing is not None:
            return existing
        # 生成
        instance = self.model_cls()          # type: ignore[arg-type]
        self.store(instance)
        return instance

    def clear(self) -> None:
        """session_state からキーを削除"""
        st.session_state.pop(self.key, None)

    # ------------------------------------------------------------------
    # シリアライズ / デシリアライズ
    # ------------------------------------------------------------------
    def serialize(self, data: T) -> str:
        """データを JSON 文字列に変換"""
        return data.json()

    def deserialize(self, json_str: str) -> T:
        """JSON 文字列からデータを復元"""
        return self.model_cls.parse_raw(json_str)
