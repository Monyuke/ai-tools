import streamlit as st
from ai_tools.page_modules.ask.state import state_manager, AppState
from ai_tools.page_modules.ask.ui import (
    render_title,
    render_input_area,
    render_download_button,
    render_form,
    render_output,
    render_downloads,
)
from ai_tools.page_modules.ask.logic import build_message, execute_ai, apply_edits
from ai_tools.lib.st.markdown_viewer import markdown_viewer
from ai_tools.lib.st.llm_document_editor import LLMDocumentEditor
from ai_tools.lib.st.state_manager.ui import state_manager_ui


# 1. UI
render_title()
user_text, file_paths, sourcemap_paths = render_input_area()
render_download_button(user_text, file_paths, sourcemap_paths)

# 2. Form & actions
submitted_exec, submitted_plan, submitted_cmd = render_form()

# 3. State 保存
if submitted_exec or submitted_plan or submitted_cmd:
    state = state_manager.get_or_create()
    state.user_input = user_text
    state.file_paths_input = file_paths
    state.sourcemap_paths_input = sourcemap_paths
    state_manager.store(state)

    # 4. メッセージ作成
    message = build_message(user_text, file_paths, sourcemap_paths, submitted_plan)

    # 5. AI 呼び出し
    if submitted_exec or submitted_plan:
        result = execute_ai(message)
        state.ai_message = result
    elif submitted_cmd:
        edit_list = apply_edits(message)
        # ここで編集結果を文字列化して state.ai_message に格納
        result = ""
        for ed in edit_list:
            result += f"- EditData: {ed.file} ({ed.type})\n"
            result += f"  search:\n```\n{ed.search}\n```\n"
            result += f"  replace:\n```\n{ed.replace}\n```\n"
            result += "\n----\n"
        state.ai_message = result

    state_manager.store(state)

# 6. 出力表示
state = state_manager.get_or_create()


def on_doc_change(doc: str):
    state.ai_message = doc
    state_manager.store(state)
    st.rerun()


LLMDocumentEditor(
    document=state.ai_message,
    extra_context=build_message("", file_paths, sourcemap_paths, False),
    on_change=on_doc_change,
).render()
st.space("large")

# markdown_viewer(state.ai_message, on_change=None)  # 編集タブは不要
render_downloads(state)

# 0. State‑manager UI
state_manager_ui(state_manager)
