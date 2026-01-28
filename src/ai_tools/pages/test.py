import streamlit as st
import time

if st.button("処理開始"):
    with st.status("処理を実行中...", expanded=True) as status:
        st.write("ステップ1: データ読み込み中...")
        time.sleep(2)  # 重い処理の代わり
        st.write("✓ データ読み込み完了")
        
        st.write("ステップ2: データ変換中...")
        time.sleep(3)  # 重い処理の代わり
        st.write("✓ データ変換完了")
        
        st.write("ステップ3: 結果保存中...")
        time.sleep(2)  # 重い処理の代わり
        st.write("✓ 結果保存完了")
        
        status.update(label="処理完了！", state="complete", expanded=False)