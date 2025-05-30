import chromadb # version < 0.4.0
from chromadb.config import Settings
import sentence_transformers
from tasks.t_ToolQA.t_text_task.utils import CHROMA_DB_BASE_DIR

chroma_client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=str(CHROMA_DB_BASE_DIR / 'scirex-v2'),
    ))

CHROMA_DB = chroma_client.get_collection(name='all')
MODEL = sentence_transformers.SentenceTransformer("sentence-transformers/all-mpnet-base-v2", local_files_only=True)
