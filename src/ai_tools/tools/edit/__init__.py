# src/ai_tools/tools/edit/__init__.py
from .edit_data import EditData, EditType
from typing import List
from ai_tools.lib.llm import structured_ask
import os
from .utils import edit_one
from pydantic import BaseModel, Field


class Result(BaseModel):
    edit_data_list: List[EditData] = Field(default=[], description="EditDataのリスト")


def build_edit_data_list(
    user_prompt: str, model: str = "gpt-oss:20b", reasoning="low"
) -> List[EditData]:
    """
    ユーザーのプロンプトを受け取り、LLM で EditData のリストを生成。
    """
    print('########################################')
    print('########################################')
    print('user_prompt:' + str(user_prompt))
    print('########################################')
    print('########################################')
    for i in range(5):
        # LLM に渡すプロンプト例
        prompt = f"""
計画を実行せよ。
1. 変更対象のファイルは絶対パスで指定してください。
2. 置換対象文字列は完全一致で指定してください。新規作成や削除の場合は空文字列にしてください。
3. 置換後文字列は削除の場合は空文字列にしてください。
4. type は Create, Edit, Delete のいずれかにしてください。

フォーマット:
- EditData
  - file: 絶対パス
  search: 置換対象（完全一致）。複数行可。必ず元ファイル内の記述でなければならない。
  replace: 置換後文字列。複数行可。
  type: EditType
- EditType
  - Create
  - Edit
  - Delete

計画:
{user_prompt}
    """
        print('prompt:' + str(prompt))
        # 生成結果は EditData のリスト
        result = structured_ask(
            model=model, message=prompt, schema=Result, reasoning=reasoning
        )
        print('result:' + str(result))
        return result.edit_data_list
    raise ValueError("build_edit_data_list:試行回数が限界に達しました。")


def edit_all(edits: List[EditData]) -> None:
    for edit in edits:
        edit_one(edit)
