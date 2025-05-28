# ingest_files.py

import os

EXCLUDE_DIRS = {".git", "tests", "__pycache__"}

def list_all_files(root):
    """Yield all files we care about (.py + key configs/docs)."""
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in files:
            if fname.endswith(".py") or fname in {"settings.py", "urls.py", "README.rst"}:
                yield os.path.join(dirpath, fname)

def list_py_files(root):
    """Yield only .py files (for AST parsing)."""
    for path in list_all_files(root):
        if path.endswith(".py"):
            yield path
