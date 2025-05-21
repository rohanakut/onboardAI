# parse_defs.py

import ast
from ingest import list_py_files

def extract_defs(source_code):
    """Return list of class/function definitions with names, docstrings, and line numbers."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []   # Skip files with syntax errors or non-Python content
    defs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            defs.append({
                "type": type(node).__name__,
                "name": node.name,
                "lineno": node.lineno,
                "doc": ast.get_docstring(node) or ""
            })
    return defs

if __name__ == "__main__":
    for path in list_py_files("."):
        with open(path, encoding="utf-8") as f:
            src = f.read()
        definitions = extract_defs(src)
        if definitions:
            print(f"\nFile: {path}")
            for d in definitions:
                print(f"  {d['type']} {d['name']} (line {d['lineno']})")
