from pydantic import BaseModel, Field
from enum import Enum
from typing import List


class Edit(BaseModel):
    search: str = Field(
        default="", description="置換対象（完全一致）。複数行可。"
    )  # 置換対象（完全一致）
    replace: str = Field(
        default="", description="置換後文字列。複数行可。"
    )  # 置換後文字列


class MultiEditResponse(BaseModel):
    edit_list: List[Edit] = Field(default=[], description="編集データのリスト")
