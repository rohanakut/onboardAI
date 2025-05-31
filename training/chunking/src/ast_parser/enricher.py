import ast
import inspect
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)  # onboardai.parsing.enricher

class ASTMetadataEnricher:
    """
    SRP: Given a minimal chunk + the full file text, enrich it with:
      - module_doc (module-level docstring, if any)
      - imports  (all top-level import names)
      - doc      (per-node docstring)
      - signature (function signature if node is a function)
      - decorators (list of decorator names/expressions)
      - calls     (all simple Name-based calls inside node)
      - complexity (count of If/For/While/Try/With in node)
    If chunk['type']=='TextFile', fill in defaults and return.
    """

    def enrich(self, chunk: Dict, full_source: str) -> Dict:
        # If non-Python TextFile chunk, attach minimal defaults & return
        if chunk["type"] == "TextFile":
            chunk.update({
                "doc":         "",
                "module_doc":  "",
                "imports":     [],
                "signature":   "",
                "decorators":  [],
                "calls":       [],
                "complexity": 0,
            })
            logger.debug(f"[enrich] Enriched TextFile chunk for '{chunk['path']}'")
            return chunk

        path = chunk["path"]
        logger.info(f"[enrich] Enriching {chunk['type']} '{chunk['name']}' @ {path}:{chunk['lineno']}")

        # 1) Parse full module AST
        try:
            tree = ast.parse(full_source)
        except SyntaxError as e:
            logger.error(f"[enrich] SyntaxError in full_source of '{path}': {e}")
            chunk.update({
                "module_doc": "",
                "imports":    [],
                "doc":        "",
                "signature":  "",
                "decorators": [],
                "calls":      [],
                "complexity": 0,
            })
            return chunk

        # 2) Module-level docstring
        module_doc = ast.get_docstring(tree) or ""
        # 3) Collect top-level imports (just module names)
        imports = [
            node.names[0].name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
        ]
        logger.debug(f"[enrich] module_doc length={len(module_doc)}; imports={imports}")

        # 4) Find the exact AST node (FunctionDef/ClassDef) by name & lineno
        target_node = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == chunk["name"] and node.lineno == chunk["lineno"]:
                    target_node = node
                    break

        if target_node is None:
            logger.warning(f"[enrich] No AST node found matching '{chunk['name']}' @ lineno {chunk['lineno']} in '{path}'")

        # 5) Node-level docstring
        node_doc = ast.get_docstring(target_node) if target_node else ""
        if node_doc:
            logger.debug(f"[enrich] node_doc length={len(node_doc)} for '{chunk['name']}'")

        # 6) Signature extraction (only for functions)
        signature_str = ""
        if isinstance(target_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            try:
                mini_mod = ast.Module([target_node], [])
                code_obj = compile(mini_mod, filename="<ast>", mode="exec")
                namespace = {}
                exec(code_obj, namespace)
                fn = namespace.get(chunk["name"])
                signature_str = str(inspect.signature(fn))
                logger.debug(f"[enrich] signature for '{chunk['name']}': {signature_str}")
            except Exception as e:
                logger.warning(f"[enrich] Could not compute signature for '{chunk['name']}': {e}")
                signature_str = "unknown"

        # 7) Decorators
        decos: List[str] = []
        if target_node:
            for d in getattr(target_node, "decorator_list", []):
                if isinstance(d, ast.Name):
                    decos.append(d.id)
                else:
                    try:
                        decos.append(ast.unparse(d))
                    except Exception:
                        decos.append(repr(d))
        logger.debug(f"[enrich] decorators for '{chunk['name']}': {decos}")

        # 8) Function calls inside this node (simple Name-based)
        calls = set()
        if target_node:
            for n in ast.walk(target_node):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                    calls.add(n.func.id)
        logger.debug(f"[enrich] calls inside '{chunk['name']}': {calls}")

        # 9) Cyclomatic-complexity proxy (count certain AST nodes)
        complexity = 0
        if target_node:
            for n in ast.walk(target_node):
                if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                    complexity += 1
        logger.debug(f"[enrich] complexity for '{chunk['name']}': {complexity}")

        # 10) Merge into a fresh dict
        enriched = dict(chunk)
        enriched.update({
            "doc":         node_doc or "",
            "module_doc":  module_doc,
            "imports":     imports,
            "signature":   signature_str,
            "decorators":  decos,
            "calls":       list(calls),
            "complexity":  complexity,
        })
        return enriched
