import os
from datetime import datetime
from .path import normalize_path, expand_path
from .time import format_relative_time
import ast

def read_files_content(file_paths_text: str, add_line_numbers: bool = False) -> str:
    """ファイルパステキストから内容を読み込み、マークダウンで返す
    
    Args:
        file_paths_text: ファイルパスのテキスト(改行区切り)
        add_line_numbers: 行番号を付けるかどうか(デフォルト: False)
    """
    if not file_paths_text.strip():
        return ""

    content = ""
    input_paths = [normalize_path(p) for p in file_paths_text.strip().split('\n') if p.strip()]

    all_files = []
    for p in input_paths:
        all_files.extend(expand_path(p))

    # 重複除去
    seen, unique_files = set(), []
    for f in all_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)

    files_with_mtime = []
    for path in unique_files:
        try:
            mtime = os.path.getmtime(path)
        except Exception:
            mtime = 0
        files_with_mtime.append((path, mtime))

    latest_mtime = max((m for _, m in files_with_mtime), default=0)

    for path, mtime in files_with_mtime:
        is_latest = (mtime == latest_mtime and mtime > 0)
        try:
            if mtime > 0:
                relative = format_relative_time(mtime)
                abs_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                latest_mark = "[LATEST] " if is_latest else ""
                time_info = f"{latest_mark}[{relative}: {abs_time}]"
            else:
                time_info = "[timestamp unavailable]"

            with open(path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            if add_line_numbers:
                lines = file_content.splitlines()
                numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
                file_content = '\n'.join(numbered_lines)
            
            content += f"\n\n--- File: {path} {time_info} ---\n{file_content}"
        except Exception as e:
            content += f"\n\n--- File: {path} ---\n[Error: {e}]"
    return content

def generate_sourcemap(file_paths_text: str) -> str:
    """Python ファイルのソースマップを生成する"""
    if not file_paths_text.strip():
        return ""

    content = ""
    input_paths = [normalize_path(p) for p in file_paths_text.strip().split('\n') if p.strip()]

    all_files = []
    for p in input_paths:
        all_files.extend(expand_path(p))

    seen, unique_files = set(), []
    for f in all_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)

    for path in unique_files:
        if not path.endswith('.py'):
            continue

        content += f"\n\n--- Sourcemap for: {path} ---\n"
        try:
            with open(path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            line_count = len(source_code.splitlines())
            content += f"File: {path}\nLines: {line_count}\n\n"

            try:
                tree = ast.parse(source_code)
            except SyntaxError as e:
                content += f"[Syntax Error: {e}]\n"
                continue

            # Import
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = f"{alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                        imports.append((name, node.lineno))
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        name = f"from {module} import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                        imports.append((name, node.lineno))

            if imports:
                content += "### Imports\n"
                for name, lineno in imports:
                    content += f"- {name} (line {lineno})\n"
                content += "\n"

            # Classes
            classes = []
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    cls = {
                        'name': node.name,
                        'lineno': node.lineno,
                        'end_lineno': node.end_lineno,
                        'docstring': ast.get_docstring(node),
                        'methods': [],
                        'attributes': []
                    }
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            cls['methods'].append(item.name)
                        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            attr_name = item.target.id
                            attr_type = ast.unparse(item.annotation) if hasattr(ast, 'unparse') else str(item.annotation)
                            cls['attributes'].append(f"{attr_name}: {attr_type}")
                    classes.append(cls)

            if classes:
                content += "### Classes\n"
                for cls in classes:
                    content += f"- {cls['name']} (line {cls['lineno']}-{cls['end_lineno']})\n"
                    if cls['docstring']:
                        content += f"  \"\"\"{cls['docstring']}\"\"\"\n"
                    if cls['attributes']:
                        content += "  Attributes:\n"
                        for attr in cls['attributes']:
                            content += f"    - {attr}\n"
                    if cls['methods']:
                        content += f"  Methods: {', '.join(cls['methods'])}\n"
                    content += "\n"

            # Functions
            functions = []
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    args = []
                    for arg in node.args.args:
                        arg_str = arg.arg
                        if arg.annotation:
                            arg_type = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else str(arg.annotation)
                            arg_str += f": {arg_type}"
                        args.append(arg_str)
                    return_type = ""
                    if node.returns:
                        return_type = " -> " + (ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns))
                    functions.append({
                        'name': node.name,
                        'args': ', '.join(args),
                        'return_type': return_type,
                        'lineno': node.lineno,
                        'end_lineno': node.end_lineno,
                        'docstring': ast.get_docstring(node)
                    })

            if functions:
                content += "### Functions\n"
                for func in functions:
                    content += f"- {func['name']}({func['args']}){func['return_type']} (line {func['lineno']}-{func['end_lineno']})\n"
                    if func['docstring']:
                        content += f"  \"\"\"{func['docstring']}\"\"\"\n"
                    content += "\n"

            # Global vars
            global_vars = []
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            global_vars.append((target.id, node.lineno))
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    var_name = node.target.id
                    var_type = ast.unparse(node.annotation) if hasattr(ast, 'unparse') else str(node.annotation)
                    global_vars.append((f"{var_name}: {var_type}", node.lineno))

            content += "### Global Variables\n"
            if global_vars:
                for var, lineno in global_vars:
                    content += f"- {var} (line {lineno})\n"
            else:
                content += "- [None found]\n"

        except Exception as e:
            content += f"[Error analyzing file: {e}]\n"
    return content