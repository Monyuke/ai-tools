## filepaths

```
D:\monyuke-dev\ai-tools\src\ai_tools\lib\llm_text_editor\spec.md
D:\monyuke-dev\ai-tools\src\ai_tools\lib\llm_text_editor\type.py
```

## output

## 1. 目的
`ai_tools.lib.llm_text_editor` パッケージは、LLM（Large Language Model）から返ってくる編集指示（`Edit`）を受け取り、テキストデータに対して一括で置換を行うクラス `LLMTextEditor` を提供します。  
主な機能は以下の通りです。

| 機能 | 内容 |
|------|------|
| **データ保持** | `data: str` を保持し、編集前後のテキストを保持 |
| **編集適用** | `apply_edits(edits: List[Edit])` で複数の `Edit` を順に適用 |
| **検索・置換** | `search` が完全一致であることを前提に、複数行にまたがる検索文字列を置換 |
| **エラーハンドリング** | 置換対象が見つからない場合は警告を出す |
| **テスト** | 単体テストで正しい置換が行われることを確認 |

## 2. ディレクトリ構成
```
src/
└─ ai_tools/
   └─ lib/
      └─ llm_text_editor/
          ├─ __init__.py
          ├─ type.py          # Editモデル
          ├─ editor.py        # LLMTextEditorクラス
          └─ tests/
              └─ test_editor.py
```

## 3. 実装詳細

### 3.1 `__init__.py`
```python
from .editor import LLMTextEditor
from .type import Edit

__all__ = ["LLMTextEditor", "Edit"]
```

### 3.2 `type.py`
既に実装済み。`Edit` は `search` と `replace` を持つ `BaseModel`。

### 3.3 `editor.py`
```python
from __future__ import annotations
from typing import List
import logging
from .type import Edit

logger = logging.getLogger(__name__)

class LLMTextEditor:
    """
    LLMから返ってくる編集指示をテキストに適用するクラス。

    Attributes
    ----------
    data : str
        編集対象のテキスト。初期化時に渡す。
    """

    def __init__(self, data: str):
        self.data = data

    def apply_edits(self, edits: List[Edit]) -> str:
        """
        複数の Edit を順に適用し、最終的なテキストを返す。

        Parameters
        ----------
        edits : List[Edit]
            置換指示のリスト。順序は重要。

        Returns
        -------
        str
            置換後のテキスト。
        """
        result = self.data
        for idx, edit in enumerate(edits, start=1):
            if edit.search == "":
                logger.warning(f"Edit #{idx} has empty search string; skipping.")
                continue
            if edit.search not in result:
                logger.warning(
                    f"Edit #{idx}: search string not found in current data."
                )
                continue
            result = result.replace(edit.search, edit.replace)
            logger.debug(
                f"Edit #{idx}: replaced '{edit.search}' with '{edit.replace}'."
            )
        self.data = result
        return result
```

#### 3.3.1 重要ポイント
- **完全一致検索**：`str.replace` を使用。`search` が複数行にまたがる場合でも問題なく置換できる。
- **順序保持**：リストの順序で適用。後続の置換が前置換に影響するケースを想定。
- **ログ**：`logging` を使い、見つからない場合や空文字列の場合に警告を出す。テスト時は `logging` を抑制可能。

### 3.4 テスト (`tests/test_editor.py`)
```python
import pytest
from ai_tools.lib.llm_text_editor import LLMTextEditor, Edit

def test_single_replacement():
    editor = LLMTextEditor("Hello world")
    edits = [Edit(search="world", replace="Python")]
    result = editor.apply_edits(edits)
    assert result == "Hello Python"

def test_multiple_replacements():
    editor = LLMTextEditor("foo bar foo")
    edits = [
        Edit(search="foo", replace="baz"),
        Edit(search="bar", replace="qux")
    ]
    result = editor.apply_edits(edits)
    assert result == "baz qux baz"

def test_multiline_replacement():
    editor = LLMTextEditor("line1\nline2\nline3")
    edits = [Edit(search="line1\nline2", replace="first two lines")]
    result = editor.apply_edits(edits)
    assert result == "first two lines\nline3"

def test_not_found():
    editor = LLMTextEditor("abc")
    edits = [Edit(search="xyz", replace="123")]
    result = editor.apply_edits(edits)
    assert result == "abc"  # unchanged

def test_empty_search():
    editor = LLMTextEditor("abc")
    edits = [Edit(search="", replace="123")]
    result = editor.apply_edits(edits)
    assert result == "abc"  # unchanged
```

## 4. 追加機能（任意）
- **正規表現置換**：`Edit` に `use_regex: bool` を追加し、必要に応じて `re.sub` を使用。
- **差分表示**：`apply_edits` が返す前後の差分を `difflib` で取得。
- **Undo 機能**：編集前の状態を保持し、`undo()` で戻せるように。

## 5. 実装手順

1. **ディレクトリ作成**  
   `src/ai_tools/lib/llm_text_editor/` を作成し、`__init__.py`, `type.py`, `editor.py`, `tests/test_editor.py` を配置。

2. **`type.py` の確認**  
   既存コードをそのまま使用。

3. **`editor.py` の実装**  
   上記コードを貼り付け、`logging` の設定を確認。

4. **テスト実行**  
   `pytest` で `tests/test_editor.py` を実行し、全テストが通ることを確認。

5. **ドキュメント**  
   `README.md` などに簡単な使用例を追記。

## 6. まとめ
- `LLMTextEditor` はシンプルに `data` を保持し、`apply_edits` で `Edit` リストを順に適用。
- 置換は完全一致で行い、複数行もそのまま扱える。
- テストで基本的なケースを網羅し、エラー時の挙動も確認。

これで「LLMを使ってテキストを編集するクラス」の要件を満たす実装が完成します。
