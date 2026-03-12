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

# Global variable to cache the FAISS index
_vector_store = None


async def search_faiss(query: str) -> str:
    """Tool function: Searches the FAISS index using OpenAI embeddings."""
    global _vector_store

    if not os.path.exists(FAISS_INDEX_PATH):
        return "Error: Local index not found."

    if _vector_store is None:
        # Use a local, high-quality embedding model (runs on CPU)
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        _vector_store = FAISS.load_local(
            FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
        )

    results = _vector_store.similarity_search(query, k=3)

    sections = []
    for res in results:
        source = res.metadata.get("source", "Unknown")
        page = res.metadata.get("page", "?")
        sections.append(f"[Source: {source}, Page: {page}]\n{res.page_content}")
    return (
        "\n---\n".join(sections)
        if sections
        else "No relevant information found in the document store."
    )
