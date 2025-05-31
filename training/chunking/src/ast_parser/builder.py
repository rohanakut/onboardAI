from typing import List, Dict
from splitter import ASTSplitter
from enricher import ASTMetadataEnricher


class ASTChunkBuilder:
    """
    Coordinator (Facade):
      - Instantiates ASTSplitter and ASTMetadataEnricher.
      - Exposes a single `build(...)` method that:
         1. Uses ASTSplitter to get raw chunks.
         2. Uses ASTMetadataEnricher to enrich each chunk.
         3. Returns the final list of enriched chunks.
    """

    def __init__(self):
        self.splitter = ASTSplitter()
        self.enricher = ASTMetadataEnricher()

    def build(self, source_code: str, path: str) -> List[Dict]:
        """
        1. Call splitter.split(source_code, path) → list of bare chunks
        2. For each chunk, call enricher.enrich(chunk, source_code)
        3. Return the list of enriched chunks
        """
        raw_chunks = self.splitter.split(source_code, path)
        # print("Raw chunks:",raw_chunks)
        enriched_chunks = [self.enricher.enrich(chunk, source_code) for chunk in raw_chunks]
        # print("Enriched chunks:",enriched_chunks)
        return enriched_chunks
