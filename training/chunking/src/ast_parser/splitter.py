import ast
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)  # onboardai.parsing.splitter

class ASTSplitter:
    """
    SRP: Given raw text + path, split into minimal chunks.
      - If *.py → one chunk per top-level FunctionDef/ClassDef
      - Else     → one chunk of type 'TextFile' containing full text
    """

    def __init__(self, node_types: List[type] = None):
        self.node_types = node_types or [ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]
        logger.debug(f"ASTSplitter init with node_types={self.node_types}")

    def split(self, source: str, path: str) -> List[Dict]:
        # Determine file extension
        _, ext = os.path.splitext(path.lower())
        if ext != ".py":
            # Non-Python: emit a single TextFile chunk
            logger.info(f"[split] Non-Python file '{path}', emitting one TextFile chunk")
            lines = source.splitlines()
            return [{
                "path":       path,
                "type":       "TextFile",
                "name":       os.path.basename(path),
                "lineno":     1,
                "end_lineno": len(lines),
                "source":     source,
            }]

        # Python: real AST parse
        logger.info(f"[split] Splitting Python file '{path}'")
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            logger.error(f"[split] SyntaxError parsing '{path}': {e}")
            return []

        lines = source.splitlines()
        chunks: List[Dict] = []

        # Only top-level nodes under tree.body
        for node in tree.body:
            if type(node) in self.node_types:
                start = node.lineno - 1
                end = getattr(node, "end_lineno", len(lines))
                node_src = "\n".join(lines[start:end])

                chunk = {
                    "path":       path,
                    "type":       type(node).__name__,
                    "name":       node.name,
                    "lineno":     node.lineno,
                    "end_lineno": end,
                    "source":     node_src,
                }
                chunks.append(chunk)
                logger.debug(f"[split] Found {chunk['type']} '{chunk['name']}' @ {chunk['lineno']}-{chunk['end_lineno']}")

        logger.info(f"[split] Returning {len(chunks)} Python chunks from '{path}'")
        return chunks
