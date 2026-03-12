import os
import pathlib
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

load_dotenv(override=True)
assert os.getenv(
    "OPENAI_API_KEY"
), f"FATAL ERROR: {pathlib.Path(__file__).name} ->  OPENAI_API_KEY not defined!"

FAISS_INDEX_PATH = pathlib.Path(__file__).parent.parent / "faiss_index"


async def search_faiss(query: str) -> str:
    """Tool function: Searches the FAISS index using OpenAI embeddings."""
    if not os.path.exists(FAISS_INDEX_PATH):
        return "Error: Local index not found."

    # Use a local, high-quality embedding model (runs on CPU)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    db = FAISS.load_local(
        FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
    )
    results = db.similarity_search(query, k=3)

    return "\n---\n".join([res.page_content for res in results])
