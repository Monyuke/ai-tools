import streamlit as st

# タイトル・見出し
st.title("Web検索")
user_text = st.text_input("名前を入力してください")

if st.button("クリック"):
    st.write("ボタンが押されました")
