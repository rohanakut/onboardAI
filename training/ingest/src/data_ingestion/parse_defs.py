from src.data_ingestion.ingest_files import list_py_files
from data_ingestion.utils.get_class_list import extract_defs


class ParseDefs():
    def __init__(self, path):
        self.path = path

    def parse_directories(self):
        for path in list_py_files("."):
            with open(path, encoding="utf-8") as f:
                src = f.read()
            definitions = extract_defs(src)
            if definitions:
                print(f"\nFile: {path}")
                for d in definitions:
                    print(f"  {d['type']} {d['name']} (line {d['lineno']})")
