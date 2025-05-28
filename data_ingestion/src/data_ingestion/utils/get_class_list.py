import ast

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