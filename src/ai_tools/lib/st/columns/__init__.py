import streamlit as st
from typing import List, Callable, Optional, Union


def columns(
    funcs: List[Callable], widths: Optional[Union[int, List[int]]] = None, **kwargs
):
    """
    Create columns and execute each function in its context.
    """
    # 1. streamlit.columns で列を作成
    if widths is None:
        cols = st.columns(len(funcs), **kwargs)
    else:
        cols = st.columns(widths, **kwargs)

    # 2. 各列に対して関数を実行
    for col, func in zip(cols, funcs):
        with col:
            func(col)

    return cols
