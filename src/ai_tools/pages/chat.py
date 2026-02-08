import streamlit as st
from ai_tools.lib.llm import chat

st.title("Chat")

# システムプロンプト（ハードコード）
SYSTEM_PROMPT = ""  # 空の場合は追加されない

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "editing_index" not in st.session_state:
    st.session_state.editing_index = None
if "deleting_index" not in st.session_state:
    st.session_state.deleting_index = None

# 既存のメッセージを表示
for idx, message in enumerate(st.session_state.messages):
    # システムメッセージは表示しない
    if message["role"] == "system":
        continue
        
    with st.chat_message(message["role"]):
        # 編集モードかどうか
        if st.session_state.editing_index == idx:
            # 編集フォーム
            new_content = st.text_area(
                "メッセージを編集",
                value=message["content"],
                key=f"edit_{idx}"
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("保存", key=f"save_{idx}"):
                    st.session_state.messages[idx]["content"] = new_content
                    st.session_state.editing_index = None
                    st.rerun()
            with col2:
                if st.button("キャンセル", key=f"cancel_{idx}"):
                    st.session_state.editing_index = None
                    st.rerun()
        # 削除確認モードかどうか
        elif st.session_state.deleting_index == idx:
            st.warning("このメッセージを削除しますか？")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("削除する", key=f"confirm_delete_{idx}", type="primary"):
                    st.session_state.messages.pop(idx)
                    st.session_state.deleting_index = None
                    st.rerun()
            with col2:
                if st.button("キャンセル", key=f"cancel_delete_{idx}"):
                    st.session_state.deleting_index = None
                    st.rerun()
        else:
            # 通常表示
            col1, col2, col3 = st.columns([10, 1, 1])
            with col1:
                st.markdown(message["content"])
            with col2:
                if st.button("✏️", key=f"edit_btn_{idx}", help="編集"):
                    st.session_state.editing_index = idx
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"delete_{idx}", help="削除"):
                    st.session_state.deleting_index = idx
                    st.rerun()

# ユーザー入力
if prompt := st.chat_input("メッセージを入力"):
    # システムプロンプトを追加（空でなければ、かつまだ追加されていなければ）
    if SYSTEM_PROMPT and (not st.session_state.messages or st.session_state.messages[0]["role"] != "system"):
        st.session_state.messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    
    # ユーザーメッセージを追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # LLMに送信（chat関数は全履歴を {"role": ..., "content": ...} 形式で返す）
    st.session_state.messages = chat(
        model="gpt-oss:20b",
        messages=st.session_state.messages,
        reasoning="low",
        tools=[]
    )
    
    # 再描画
    st.rerun()