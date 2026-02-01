import streamlit as st
from .state import AppState
from .logic import build_message


def render_title():
    st.title("ASK")


def render_input_area():
    user_text = st.text_area("内容", value="", key="user_text_main")
    file_paths = st.text_area(
        "ファイルパス（1行に1つ）",
        value="",
        key="file_paths_main",
        help="読み込みたいファイルのパスを1行ごとに入力してください。glob形式（*, **, ?）にも対応しています",
    )
    sourcemap_paths = st.text_area(
        "ソースマップ用ファイルパス（1行に1つ）",
        value="",
        key="sourcemap_paths_main",
        help="ソースマップを生成したいファイルのパスを1行ごとに入力してください。glob形式（*, **, ?）にも対応しています",
    )
    return user_text, file_paths, sourcemap_paths


def render_download_button(user_text, file_paths, sourcemap_paths):
    if user_text or file_paths or sourcemap_paths:
        md = build_message(user_text, file_paths, sourcemap_paths, False)

        st.download_button(
            "Download Input with Files",
            data=md,
            file_name="input_with_files.md",
            mime="text/plain",
            key="download_input_files",
        )


def render_form():
    with st.form("ask_form"):
        st.write("上記の内容でAIに問い合わせる場合は以下のボタンを押してください")
        col1, col2, col3 = st.columns(3)
        with col1:
            submitted_exec = st.form_submit_button("実行")
        with col2:
            submitted_plan = st.form_submit_button("計画")
        with col3:
            submitted_cmd = st.form_submit_button("適用")
    return submitted_exec, submitted_plan, submitted_cmd


def render_output(ai_message):
    if ai_message:
        st.markdown(ai_message)
        st.code(ai_message, "markdown")


def render_downloads(state: AppState):
    # ここでは state_manager から取得した状態を使う
    input_md = ""
    if state.user_input:
        input_md += f"## user_text\n\n```\n{state.user_input}\n```\n\n"
    if state.file_paths_input:
        input_md += f"## filepaths\n\n```\n{state.file_paths_input}\n```\n"
    if state.sourcemap_paths_input:
        input_md += f"\n## sourcemap_paths\n\n```\n{state.sourcemap_paths_input}\n```\n"

    combined_md = input_md
    if state.ai_message:
        combined_md = build_message(
            state.user_input, state.file_paths_input, state.sourcemap_paths_input, False
        )
        combined_md += f"\n## output\n\n{state.ai_message}\n"

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
            data=state.ai_message,
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
