import ast
from typing import List, Dict


class ASTSplitter:
    """
    Single Responsibility:
      - Take raw Python source text and a file path.
      - Return a list of minimal chunks (one per top-level FunctionDef or ClassDef),
        each containing only:
         * path, type, name, lineno, end_lineno, source
    """

    def __init__(self, node_types: List[type] = None):
        # If no node_types provided, default to top-level functions & classes.
        self.node_types = node_types or [ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]

    def split(self, source: str, path: str) -> List[Dict]:
        """
        Parse `source` into an AST, walk only top-level nodes in tree.body,
        and for each matching node type, capture its minimal chunk data.
        """
        try:
            tree = ast.parse(source)
        except SyntaxError:
            # If code cannot be parsed, return an empty list (no chunks).
            return []

        lines = source.splitlines()
        chunks: List[Dict] = []

        # Only consider nodes at the module’s top level (tree.body).
        for node in tree.body:
            if type(node) in self.node_types:
                start = node.lineno - 1
                end = getattr(node, "end_lineno", len(lines))
                node_source = "\n".join(lines[start:end])

                chunks.append({
                    "path":       path,
                    "type":       type(node).__name__,
                    "name":       node.name,
                    "lineno":     node.lineno,
                    "end_lineno": end,
                    "source":     node_source,
                })

        return chunks
