import os
import glob

def normalize_path(path: str) -> str:
    """パスを正規化する"""
    path = path.strip().strip('"').strip("'")
    return os.path.normpath(path)

def expand_path(path: str) -> list[str]:
    """glob パターンを展開してファイルリストを返す"""
    if any(c in path for c in ('*', '?', '[')):
        matches = glob.glob(path, recursive=True)
        return sorted([m for m in matches if os.path.isfile(m)])
    return [path]