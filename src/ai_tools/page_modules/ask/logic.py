import re
from ai_tools.lib.llm import simple_ask
from ai_tools.lib.llm_text_editor import LLMTextEditor
from ai_tools.tools.edit import build_edit_data_list, edit_all
from ai_tools.utils.file_io import read_files_content, generate_sourcemap

def build_message(user_text, file_paths, sourcemap_paths, plan_flag):
    message = user_text
    if plan_flag:
        message += "\n\n以上の要求を満たすよう計画して。"
    if sourcemap_paths.strip():
        sm = generate_sourcemap(sourcemap_paths)
        if sm:
            message += f"\n\n## Sourcemap\n{sm}"
    if file_paths.strip():
        files_md = read_files_content(file_paths)
        if files_md:
            message += f"\n\n{files_md}"
    return message

def execute_ai(message):
    return simple_ask(model="gpt-oss:20b", message=message, reasoning="low")

def apply_edits(message):
    edit_data_list = build_edit_data_list(user_prompt=message, model="gpt-oss:20b", reasoning="low")
    edit_all(edit_data_list)
    return edit_data_list