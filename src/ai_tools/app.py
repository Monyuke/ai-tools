import streamlit as st
from dataclasses import dataclass
from datetime import datetime
from ai_tools.lib.llm import simple_ask
from ai_tools.utils.path import normalize_path, expand_path
from ai_tools.utils.file_io import read_files_content, generate_sourcemap
# 既存の st_agents はそのままインポート

@dataclass
class AppState:
    ai_message: str = ""
    user_input: str = ""
    file_paths_input: str = ""
    sourcemap_paths_input: str = ""

# セッション状態初期化
if "state" not in st.session_state:
    st.session_state.state = AppState()

# ---------- UI ----------
st.title("ASK")

user_text = st.text_area("内容", value="", key="user_text_main")
file_paths = st.text_area(
    "ファイルパス（1行に1つ）",
    value="",
    key="file_paths_main",
    help="読み込みたいファイルのパスを1行ごとに入力してください。glob形式（*, **, ?）にも対応しています"
)
sourcemap_paths = st.text_area(
    "ソースマップ用ファイルパス（1行に1つ）",
    value="",
    key="sourcemap_paths_main",
    help="ソースマップを生成したいファイルのパスを1行ごとに入力してください。glob形式（*, **, ?）にも対応しています"
)

# ---------- ダウンロードボタン ----------
if user_text or file_paths or sourcemap_paths:
    md = ""
    if user_text:
        md += f"## user_text\n\n```\n{user_text}\n```\n\n"
    if file_paths:
        md += f"## filepaths\n\n```\n{file_paths}\n```\n"
    if sourcemap_paths:
        md += f"\n## sourcemap_paths\n\n```\n{sourcemap_paths}\n```\n"
        sourcemap_content = generate_sourcemap(sourcemap_paths)
        if sourcemap_content:
            md += f"\n## sourcemap\n\n```\n{sourcemap_content}\n```\n"
    if file_paths:
        files_content = read_files_content(file_paths)
        if files_content:
            md += f"\n## files_content\n{files_content}\n"

    st.download_button(
        "Download Input with Files",
        data=md,
        file_name="input_with_files.md",
        mime="text/plain",
        key="download_input_files"
    )

# ---------- AI実行 ----------
with st.form("ask_form"):
    st.write("上記の内容でAIに問い合わせる場合は以下のボタンを押してください")
    submitted = st.form_submit_button("実行")

if submitted:
    # 入力を保存
    st.session_state.state.user_input = user_text
    st.session_state.state.file_paths_input = file_paths
    st.session_state.state.sourcemap_paths_input = sourcemap_paths

    # メッセージ作成
    message = user_text

    if sourcemap_paths.strip():
        sm = generate_sourcemap(sourcemap_paths)
        if sm:
            message += f"\n\n## Sourcemap\n{sm}"

    if file_paths.strip():
        # ファイル読み込みロジックは read_files_content で済むので再利用
        files_md = read_files_content(file_paths)
        if files_md:
            message += f"\n\n{files_md}"

    # AI呼び出し
    result = simple_ask(model="gpt-oss:20b", message=message, reasoning="high")
    st.session_state.state.ai_message = result

# ---------- ダウンロード ----------
if st.session_state.state.user_input or st.session_state.state.file_paths_input or st.session_state.state.sourcemap_paths_input:
    input_md = ""
    if st.session_state.state.user_input:
        input_md += f"## user_text\n\n```\n{st.session_state.state.user_input}\n```\n\n"
    if st.session_state.state.file_paths_input:
        input_md += f"## filepaths\n\n```\n{st.session_state.state.file_paths_input}\n```\n"
    if st.session_state.state.sourcemap_paths_input:
        input_md += f"\n## sourcemap_paths\n\n```\n{st.session_state.state.sourcemap_paths_input}\n```\n"

    combined_md = input_md
    if st.session_state.state.ai_message:
        combined_md += f"\n## output\n\n{st.session_state.state.ai_message}\n"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("Download Input", data=input_md, file_name="user_input.md", mime="text/plain")
    with col2:
        st.download_button("Download Output", data=st.session_state.state.ai_message, file_name="ai_result.md", mime="text/plain")
    with col3:
        st.download_button("Download All", data=combined_md, file_name="all_result.md", mime="text/plain")

# ---------- AI応答表示 ----------
if st.session_state.state.ai_message:
    st.markdown(st.session_state.state.ai_message)
    st.code(st.session_state.state.ai_message, "markdown")