"""
rag_pipeline.py
    Runs the RAG pipeline that creates the vector store, which agent quries
"""

import os
import pathlib
from dotenv import load_dotenv


from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(override=True)
assert os.getenv(
    "OPENAI_API_KEY"
), f"FATAL ERROR: {pathlib.Path(__file__).name}: OPENAI_API_KEY not defined!"

FAISS_INDEX_PATH = pathlib.Path(__file__).parent / "faiss_index"


def build_local_index(pdf_folder: str):
    """Loads PDFs and builds a FAISS index using OpenAI Embeddings."""
    pdf_path = pathlib.Path(pdf_folder).expanduser()
    documents = []

    num_files = 0

    for file in pdf_path.glob("*.pdf"):
        loader = PyPDFLoader(str(file))
        documents.extend(loader.load())
        num_files += 1

    print(f"Loaded {num_files} PDFs from {str(pdf_path)}")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    # Use a local, high-quality embedding model (runs on CPU)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # This will call the OpenAI API to generate embeddings for your text chunks
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(FAISS_INDEX_PATH)
    print(f"✅ FAISS index (OpenAI) saved to {str(FAISS_INDEX_PATH)}")


if __name__ == "__main__":
    if not FAISS_INDEX_PATH.exists():
        pdf_folder = pathlib.Path(__file__).parent / "docs"
        print(f"Building FAISS index from files in folder {str(pdf_folder)}...", end="")
        build_local_index(pdf_folder)
        print("Done!")
    else:
        print(f"Faiss index exists at {str(FAISS_INDEX_PATH)}")
