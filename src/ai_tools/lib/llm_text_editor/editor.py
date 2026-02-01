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