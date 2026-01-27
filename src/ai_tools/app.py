import streamlit as st

st.set_page_config(
    page_title="ホームページ", page_icon="🏠"  # このページ専用のタイトル
)

# タイトル・見出し
st.title("タイトル")
st.header("ヘッダー")
st.subheader("サブヘッダー")

# テキスト
st.text("普通のテキスト")
st.write("何でも表示できる万能関数")

# Markdown
st.markdown("**太字** や *斜体* も使えます")

# コード表示
st.code("print('Hello')", language="python")
