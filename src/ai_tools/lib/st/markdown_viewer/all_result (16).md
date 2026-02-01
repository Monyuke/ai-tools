## filepaths

```
D:\monyuke-dev\ai-tools\src\ai_tools\lib\st\markdown_viewer\spec.md
```

## sourcemap_paths

```
D:\monyuke-dev\ai-tools\src\ai_tools\lib\st/**/*
```

## output

## 1. 目的  
`ai_tools.lib.st.markdown_viewer` を実装し、Streamlit アプリで **Markdown Viewer** コンポーネントを簡単に利用できるようにする。  
- 3 つのタブ（Preview / Code / Edit）を持つ  
- `body`（Markdown 文字列）を表示  
- `on_change` が渡された場合のみ Edit タブを表示し、変更時にコールバックを呼び出す  

## 2. ディレクトリ構成  
```
src/
└─ ai_tools/
   └─ lib/
      └─ st/
         └─ markdown_viewer/
            ├─ __init__.py          # ここに実装
            └─ spec.md              # 仕様書（上記）
```

## 3. 実装方針  
1. **関数ベース**  
   - `markdown_viewer(body: str, on_change: Optional[Callable[[str], Any]] = None) -> None`  
   - 返り値は不要（Streamlit の描画は副作用で行う）  

2. **タブの作成**  
   - `st.tabs(["Preview", "Code"] + (["Edit"] if on_change else []))`  
   - `st.tabs` はリストを受け取るので、`on_change` がある場合だけ Edit を追加  

3. **タブ内の描画**  
   - **Preview**: `st.markdown(body, unsafe_allow_html=True)`  
   - **Code**: `st.code(body, language="markdown")`  
   - **Edit**: `st.text_area("Edit Markdown", value=body, key="md_edit", on_change=on_change_wrapper)`  
     - `on_change_wrapper` は `on_change` を呼び出す前に `st.session_state.md_edit` から最新のテキストを取得  

4. **on_change の取り扱い**  
   - `on_change` は `Callable[[str], Any]`（引数に現在の Markdown を渡す）  
   - `on_change_wrapper` 内で `on_change(st.session_state.md_edit)` を実行  

5. **型ヒントとドキュメント**  
   - `typing` を活用し、関数のシグネチャを明確化  
   - docstring でパラメータと挙動を説明  

6. **テスト**  
   - `pytest` で簡易テストを作成（`st` のモックは `streamlit.testing` などを利用）  
   - 主要ケース  
     - `on_change=None` → Edit タブが無い  
     - `on_change` がある → Edit タブが表示され、変更時にコールバックが呼ばれる  

## 4. コード例（`__init__.py`）  
```python
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
```

## 5. 追加の考慮点  
- **セッション管理**  
  - `edit_key` を `id(body)` で生成しているので、同じ `body` 文字列でも別インスタンスで衝突しない。  
- **安全性**  
  - `st.markdown` で `unsafe_allow_html=True` を設定しているが、外部入力を扱う場合は XSS 対策を検討。  
- **拡張性**  
  - 将来的に `language` パラメータを追加して Code タブのハイライト言語を指定できるようにする。  

## 6. テスト例（`tests/test_markdown_viewer.py`）  
```python
import pytest
from unittest.mock import MagicMock

import streamlit.testing.v1 as stv

from ai_tools.lib.st.markdown_viewer import markdown_viewer


def test_viewer_without_edit():
    """Edit タブが無いことを確認"""
    with stv.using_streamlit():
        markdown_viewer("Hello **world**")
        # tabs の数は 2
        assert len(stv.get_all("tabs")) == 2
        # Edit タブは存在しない
        assert not any(t.label == "Edit" for t in stv.get_all("tabs"))


def test_viewer_with_edit_and_callback():
    """Edit タブが表示され、変更時にコールバックが呼ばれる"""
    mock_cb = MagicMock()

    with stv.using_streamlit():
        markdown_viewer("Initial", on_change=mock_cb)

        # Edit タブがある
        tabs = stv.get_all("tabs")
        assert any(t.label == "Edit" for t in tabs)

        # Edit タブ内のテキストエリアを取得
        textarea = stv.get("text_area", key="markdown_viewer_edit_0")
        # 変更をシミュレート
        textarea.set_value("Updated")
        # on_change が呼ばれたか確認
        mock_cb.assert_called_once_with("Updated")
```

## 7. まとめ  
- **シンプルな API**：`markdown_viewer(body, on_change=None)`  
- **タブベースの UI**：Preview / Code / Edit（オプション）  
- **コールバック**：Edit で変更時に外部関数を呼び出す  
- **テスト**：Streamlit のテストユーティリティで動作確認  

この設計で、Streamlit アプリに Markdown Viewer を簡単に組み込めるようになります。
