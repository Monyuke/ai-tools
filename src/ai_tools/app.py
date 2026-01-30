import streamlit as st
from textwrap import dedent
from dataclasses import dataclass
import os
import glob
from ai_tools.st_agents.web_search import st_agent_websearch
from ai_tools.st_agents.title import st_agent_title
from ai_tools.lib.llm import simple_ask

@dataclass
class AppState:
    ai_message: str = ""
    user_input: str = ""
    file_paths_input: str = ""

if "state" not in st.session_state:
    st.session_state.state = AppState()

def normalize_path(path: str) -> str:
    """パスを正規化する"""
    # 前後の空白を削除
    path = path.strip()
    # クォートを削除
    path = path.strip('"').strip("'")
    # パスを正規化（区切り文字の統一、冗長な区切り文字の削除など）
    path = os.path.normpath(path)
    return path

def expand_path(path: str) -> list[str]:
    """パスを展開する。glob形式に対応"""
    # glob パターンが含まれているか確認
    if '*' in path or '?' in path or '[' in path:
        # glob で展開
        matches = glob.glob(path, recursive=True)
        # ファイルのみを抽出してソート
        files = sorted([m for m in matches if os.path.isfile(m)])
        return files
    else:
        # 通常のファイルパスとして返す
        return [path]

def read_files_content(file_paths_text: str) -> str:
    """ファイルパステキストからファイル内容を読み込んでマークダウン形式で返す"""
    if not file_paths_text.strip():
        return ""
    
    content = ""
    input_paths = [normalize_path(p) for p in file_paths_text.strip().split('\n') if p.strip()]
    
    # 各入力パスを展開
    all_files = []
    for input_path in input_paths:
        expanded = expand_path(input_path)
        all_files.extend(expanded)
    
    # 重複を削除しつつ順序を保持
    seen = set()
    unique_files = []
    for f in all_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    
    # ファイルを読み込んで内容を追加
    for path in unique_files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            content += f"\n\n--- File: {path} ---\n{file_content}"
        except Exception as e:
            content += f"\n\n--- File: {path} ---\n[Error: {e}]"
    
    return content

st.title("ASK")

# フォーム外の入力欄（リアルタイムでダウンロード可能にするため）
user_text = st.text_area("内容", value="", key="user_text_main")
file_paths = st.text_area(
    "ファイルパス（1行に1つ）", 
    value="", 
    key="file_paths_main",
    help="読み込みたいファイルのパスを1行ごとに入力してください。glob形式（*, **, ?）にも対応しています"
)

# 入力内容+ファイル内容のダウンロードボタン（実行前でも使用可能）
if user_text or file_paths:
    input_with_files_md = ""
    if user_text:
        input_with_files_md += f"## user_text\n\n```\n{user_text}\n```\n\n"
    if file_paths:
        input_with_files_md += f"## filepaths\n\n```\n{file_paths}\n```\n"
        # ファイル内容を読み込んで追加
        files_content = read_files_content(file_paths)
        if files_content:
            input_with_files_md += f"\n## files_content\n{files_content}\n"
    
    st.download_button(
        "Download Input with Files",
        data=input_with_files_md,
        file_name="input_with_files.md",
        mime="text/plain",
        key="download_input_files"
    )

# AI実行用フォーム
with st.form("ask_form"):
    st.write("上記の内容でAIに問い合わせる場合は以下のボタンを押してください")
    submitted = st.form_submit_button("実行")

if submitted:
    # 入力内容を保存
    st.session_state.state.user_input = user_text
    st.session_state.state.file_paths_input = file_paths
    
    # ユーザー入力テキストを基本メッセージとする
    message = user_text
    
    # ファイルパスが入力されている場合、ファイルを読み込んで追加
    if file_paths.strip():
        input_paths = [normalize_path(p) for p in file_paths.strip().split('\n') if p.strip()]
        
        # 各入力パスを展開
        all_files = []
        for input_path in input_paths:
            expanded = expand_path(input_path)
            if not expanded:
                st.warning(f"パターンにマッチするファイルが見つかりません: {input_path}")
            all_files.extend(expanded)
        
        # 重複を削除しつつ順序を保持
        seen = set()
        unique_files = []
        for f in all_files:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)
        
        # ファイルを読み込んでメッセージに追加
        for path in unique_files:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                message += f"\n\n--- File: {path} ---\n{content}"
            except FileNotFoundError:
                st.error(f"ファイルが見つかりません: {path}")
                st.stop()
            except Exception as e:
                st.error(f"ファイルの読み込みに失敗しました ({path}): {e}")
                st.stop()
    
    result = simple_ask(model="gpt-oss:20b", message=message)
    st.session_state.state.ai_message = result

# AI実行後のダウンロードボタン群
if st.session_state.state.user_input or st.session_state.state.file_paths_input:
    # インプット用マークダウン
    input_md = ""
    if st.session_state.state.user_input:
        input_md += f"## user_text\n\n```\n{st.session_state.state.user_input}\n```\n\n"
    if st.session_state.state.file_paths_input:
        input_md += f"## filepaths\n\n```\n{st.session_state.state.file_paths_input}\n```\n"
    
    # インプット+アウトプット統合版
    combined_md = input_md
    if st.session_state.state.ai_message:
        combined_md += f"\n## output\n\n{st.session_state.state.ai_message}\n"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "Download Input",
            data=input_md,
            file_name="user_input.md",
            mime="text/plain",
        )
    
    with col2:
        st.download_button(
            "Download Output",
            data=st.session_state.state.ai_message,
            file_name="ai_result.md",
            mime="text/plain",
        )
    
    with col3:
        st.download_button(
            "Download All",
            data=combined_md,
            file_name="all_result.md",
            mime="text/plain",
        )

# AI応答の表示
if st.session_state.state.ai_message:
    st.markdown(st.session_state.state.ai_message)
    st.code(st.session_state.state.ai_message, "markdown")