import ast
import inspect
from typing import Dict, List


class ASTMetadataEnricher:
    """
    Single Responsibility:
      - Given a “bare” chunk (from ASTSplitter), plus the full source text,
        enrich that chunk with:
         * module-level docstring
         * per-node docstring
         * imports used in the module
         * function signature (if applicable)
         * decorators on that node
         * functions called inside that node
         * cyclomatic-complexity proxy (count of certain AST nodes)
    """

    def enrich(self, chunk: Dict, full_source: str) -> Dict:
        """
        Merge extra metadata into `chunk` and return an enriched copy.
        """
        # 1. Parse entire AST once to extract module-level doc and imports
        try:
            tree = ast.parse(full_source)
        except SyntaxError:
            # If full_source is syntactically invalid, just return chunk as-is.
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

        # Module-level docstring
        module_doc = ast.get_docstring(tree) or ""
        # Top-level imports (just module names, not alias handling)
        imports = [
            n.names[0].name
            for n in ast.walk(tree)
            if isinstance(n, ast.Import)
        ]

        # 2. Find the exact AST node that matches this chunk’s name & lineno
        target_node = None
        for node in tree.body:
            if hasattr(node, "name") \
               and node.name == chunk["name"] \
               and node.lineno == chunk["lineno"]:
                target_node = node
                break

        # If we didn’t find it at top level, we still try a full walk
        if target_node is None:
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if node.name == chunk["name"] and node.lineno == chunk["lineno"]:
                        target_node = node
                        break

        # 3. Extract node-level docstring
        node_doc = ""
        if target_node is not None:
            node_doc = ast.get_docstring(target_node) or ""

        # 4. Extract signature (only for functions; for classes, leave “unknown”)
        signature_str = ""
        if isinstance(target_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            try:
                # Compile a mini-module containing just this node, then inspect it
                mini_module = ast.Module([target_node], [])
                code_obj = compile(mini_module, filename="<ast>", mode="exec")
                namespace = {}
                exec(code_obj, namespace)
                fn = namespace.get(chunk["name"])
                signature_str = str(inspect.signature(fn))
            except Exception:
                signature_str = "unknown"
        else:
            signature_str = ""

        # 5. Extract decorators (names or full unparsed AST if complex)
        decos: List[str] = []
        if target_node is not None:
            for d in getattr(target_node, "decorator_list", []):
                if isinstance(d, ast.Name):
                    decos.append(d.id)
                else:
                    try:
                        # ast.unparse is available in Python 3.9+
                        decos.append(ast.unparse(d))
                    except Exception:
                        decos.append(repr(d))

        # 6. Extract called function names (only simple Name calls)
        calls = set()
        if target_node is not None:
            for n in ast.walk(target_node):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                    calls.add(n.func.id)

        # 7. Simple cyclomatic-complexity proxy: count certain AST nodes
        complexity = 0
        if target_node is not None:
            for n in ast.walk(target_node):
                if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                    complexity += 1

        # 8. Merge everything back into a new dict (so we don’t mutate input)
        enriched = dict(chunk)  # shallow copy of path/type/name/lineno/end_lineno/source
        enriched.update({
            "doc":         node_doc,
            "module_doc":  module_doc,
            "imports":     imports,
            "signature":   signature_str,
            "decorators":  decos,
            "calls":       list(calls),
            "complexity":  complexity,
        })
        return enriched
