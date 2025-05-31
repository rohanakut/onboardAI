# from training.chunking.src.ast_parser.builder import ASTChunkBuilder
import constants as constants
from loader import Loader

if __name__ == "__main__":
    loader = Loader(constants.file_path)
    loader.load()