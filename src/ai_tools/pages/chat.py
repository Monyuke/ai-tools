import streamlit as st
from ai_tools.lib.llm import chat

st.title("Chat")

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 既存のメッセージを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力
if prompt := st.chat_input("メッセージを入力"):
    # ユーザーメッセージを追加・表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # LLMに送信（chat関数は全履歴を {"role": ..., "content": ...} 形式で返す）
    st.session_state.messages = chat(
        model="gpt-oss:20b",
        messages=st.session_state.messages,
        reasoning="low",
        tools=[]
    )
    
    # 新しく追加されたメッセージ（最後のAI応答）を表示
    if st.session_state.messages:
        last_message = st.session_state.messages[-1]
        if last_message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(last_message["content"])