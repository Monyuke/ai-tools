# src/ai_tools/tools/edit/utils.py
import os
from pathlib import Path
from .edit_data import EditData, EditType

def edit_one(edit: EditData) -> None:
    path = Path(edit.file)
    if edit.type == EditType.DELETE:
        if path.exists():
            path.unlink()
        return

    content = ""
    if path.exists():
        content = path.read_text(encoding="utf-8")
    else:
        # Create か Edit でファイルが無い場合は空文字列で作成
        content = ""

    if edit.type == EditType.CREATE:
        # 既に存在する場合は上書き
        path.write_text(content, encoding="utf-8")
    elif edit.type == EditType.EDIT:
        if edit.search:
            content = content.replace(edit.search, edit.replace)
        path.write_text(content, encoding="utf-8")
