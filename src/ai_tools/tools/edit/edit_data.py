from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class EditType(str, Enum):
    CREATE = "Create"
    EDIT = "Edit"
    DELETE = "Delete"


class EditData(BaseModel):
    file: str  # 絶対パス
    search: str = Field(
        default="", description="置換対象（完全一致）。複数行可。"
    )  # 置換対象（完全一致）
    replace: str = Field(
        default="", description="置換後文字列。複数行可。"
    )  # 置換後文字列
    type: EditType = Field(
        default=EditType.CREATE, description="操作種別。"
    )  # 操作種別


class EditDataListResponse(BaseModel):
    edit_data_list: List[EditData] = Field(default=[], description="EditDataのリスト")
