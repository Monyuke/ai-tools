# ai_tools/lib/st/llm_document_editor/editor.py
from __future__ import annotations
import streamlit as st
from typing import Callable
from ai_tools.lib.llm_text_editor import LLMTextEditor
from ai_tools.lib.llm_text_editor.type import Edit
from ai_tools.lib.llm import simple_ask


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

    def _run_edit(self, target_text: str, prompt: str):
        """LLM に問い合わせて編集を実行"""
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
        response = simple_ask(model="gpt-oss:120b", reasoning="low", message=message)
        print("response:" + str(response))
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
        """全体レイアウトを描画（タブ形式）"""
        # タブラベルを作成
        tab_labels = ["Preview", "Code", "Edit", "AI Edit"]

        # タブを作成
        tabs = st.tabs(tab_labels)

        # Preview タブ
        with tabs[0]:
            st.markdown(self.document, unsafe_allow_html=True)

        # Code タブ
        with tabs[1]:
            st.code(self.document, language="markdown")

        # Edit タブ
        edit_key = f"llm_doc_editor_edit_{id(self.document)}"

        def _on_change_wrapper() -> None:
            """内部コールバック: 最新のテキストを取得して外部コールバックへ渡す"""
            current_text = st.session_state.get(edit_key, self.document)
            self.document = current_text
            self.on_change(current_text)

        with tabs[2]:
            st.text_area(
                label="Edit Markdown",
                value=self.document,
                height=400,
                key=edit_key,
                on_change=_on_change_wrapper,
            )

        # AI Edit タブ
        with tabs[3]:
            # 1. 編集対象テキスト
            edit_text = st.text_area(
                "Target Text",
                value="",
                height=200,
                key="ai_edit_text",
            )

            # 2. プロンプト
            prompt = st.text_area(
                "Edit Prompt",
                value="",
                height=200,
                key="ai_edit_prompt",
            )

            # 3. 実行ボタン
            if st.button("Run Edit"):
                self._run_edit(edit_text, prompt)
