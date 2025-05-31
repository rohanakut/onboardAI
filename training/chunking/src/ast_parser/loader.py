import json

from utils.converter import str_to_dict
from builder import ASTChunkBuilder

class Loader:
    def __init__(self,filename):
        self.builder = ASTChunkBuilder()
        self.filename = filename

    def load(self):
        snippet : dict
        with open(self.filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                snippet = str_to_dict(line)
                # if ".py" in snippet["path"]:
                chunks = self.builder.build(snippet["text"],snippet["path"])
                for chunk in chunks:
                    print(chunk)
                    print("")
                    print("")
                    # break