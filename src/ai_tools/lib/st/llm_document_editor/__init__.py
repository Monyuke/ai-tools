# ai_tools/lib/st/llm_document_editor/editor.py
from __future__ import annotations
import streamlit as st
from typing import Callable, Optional
from ai_tools.lib.llm_text_editor import LLMTextEditor
from ai_tools.lib.llm_text_editor.type import Edit
from ai_tools.lib.llm import structured_ask, simple_ask
from ai_tools.lib.st.markdown_viewer import markdown_viewer
from ai_tools.lib.st.state_manager import StateManager
from pydantic import BaseModel
from textwrap import dedent


class LLMDocumentEditor:
    """
    Streamlit 用 LLM Document Editor コンポーネント。

    Parameters
    ----------
    document : str
        初期ドキュメント（Markdown 文字列）。
    extra_context : str
        LLM に渡す追加コンテキスト。
    on_change : Callable[[str], None]
        編集完了時に呼び出されるコールバック。引数に修正済みドキュメントを渡す。
    """

    def __init__(
        self,
        document: str,
        on_change: Callable[[str], None],
        extra_context: str = "",
    ):
        self.document = document
        self.extra_context = extra_context
        self.on_change = on_change

        # 右カラム用の入力状態を保持
        self._state = StateManager(
            key="llm_doc_editor_state",
            model_cls=BaseModel,  # ここでは汎用 BaseModel を使う
        )

    def _render_left(self):
        """左カラム：Markdown ビューワー（編集可）"""
        st.subheader("Document")
        # 編集可能にするため on_change を渡す
        markdown_viewer(
            body=self.document,
            on_change=lambda new_body: self._handle_left_change(new_body),
        )

    def _handle_left_change(self, new_body: str):
        """左カラムで編集されたときに呼び出される"""
        self.document = new_body
        self.on_change(new_body)

    def _render_right(self):
        """右カラム：入力欄 + 実行ボタン"""
        st.subheader("Edit Controls")

        # 1. 編集対象テキスト
        edit_text = st.text_area(
            "Target Text",
            value="",
            height=200,
            key="edit_text",
        )

        # 2. プロンプト
        prompt = st.text_area(
            "Edit Prompt",
            value="",
            height=100,
            key="edit_prompt",
        )

        # 3. 実行ボタン
        if st.button("Run Edit"):
            self._run_edit(edit_text, prompt)

    def _run_edit(self, target_text: str, prompt: str):
        """LLM に問い合わせて編集を実行"""
        # structured_ask で EditResponse を取得

        message = f"""\
ユーザー指令に基づき、編集対象文字列を置換せよ。
出力は、全文ではなく置換内容のみにせよ。他の一切の応答は不要。

編集対象文字列：
{target_text}

ユーザー指令：
{prompt}

テキスト：
{self.document}
"""

        if self.extra_context:
            message += f"参考情報：\n{self.extra_context}\n\n"

        print("message:" + str(message))
        response = simple_ask(model="gpt-oss:20b", reasoning="medium", message=message)
        print('response:' + str(response))
        edit = Edit(
            search=target_text,
            replace=response,
        )

        # LLMTextEditor で実際に編集
        print("target_text:" + str(target_text))
        editor = LLMTextEditor(self.document)
        new_text = editor.apply_edits([edit])
        print("new_text:" + str(new_text))

        # 変更を反映
        self.document = new_text
        self.on_change(new_text)

    def render(self):
        """全体レイアウトを描画"""
        col_left, col_right = st.columns([2, 1])

        with col_left:
            self._render_left()

        with col_right:
            self._render_right()
