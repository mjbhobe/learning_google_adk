# Local RAG Agent (Retrieval-Augmented Generation)

This project implements a command-line intelligent agent that answers questions based on a local collection of PDF documents. The project uses Google's Agent Development Kit (ADK) alongside LangChain and FAISS for vector storage and semantic search capabilities.

The agent, powered by the `gpt-4o` model, processes user queries, retrieves relevant context from a pre-built FAISS index of local documents, and generates accurate, cited answers formatted in Markdown.

## Code Structure

```text
projects/local_rag/
├── main.py                     # Main CLI application: sets up session and interactive query loop
├── rag_pipeline.py             # Script to load PDFs, chunk text, and build the local FAISS index
├── docs/                       # Directory containing source PDF documents (the knowledge base)
├── faiss_index/                # Directory containing the generated vector database
└── local_rag_agent/
    ├── agent.py                # Defines the Google ADK LlmAgent with its instructions and tools
    └── tools.py                # Contains `search_faiss`, the tool used by the agent to query the index
```

### Components

- **`rag_pipeline.py`**: Reads all `.pdf` files from the `docs/` folder, splits the text into chunks using LangChain's `RecursiveCharacterTextSplitter`, generates embeddings with OpenAI's `text-embedding-3-small`, and stores them locally via FAISS.
- **`local_rag_agent/tools.py`**: Provides the `search_faiss` function. It lazy-loads the FAISS index to avoid redundant disk reads, performs similarity searches against user queries, and formats results with document source and page citations.
- **`local_rag_agent/agent.py`**: Configures the `LlmAgent` from Google ADK. It provides the strict system prompt instructing the model to rely solely on the retrieved documents, cite its sources, and use the `search_faiss` tool.
- **`main.py`**: The entry point. Initializes an in-memory chat session, ensures the vector store is built, and provides a continuous CLI loop (using the `rich` library) to chat with the agent until you type `exit` or `quit`.

## How to Run the App

1. **Verify your environment**:
   Make sure you have an `.env` file at the root or within your project containing your `OPENAI_API_KEY`. The dependencies (such as `langchain`, `faiss-cpu`, `google-adk`, `rich`, etc.) must be installed.

2. **Generate the Document Index**:
   Before querying the agent, you must parse the local PDFs inside the `docs/` folder into a vector database. Run the pipeline script once:
   ```bash
   uv run rag_pipeline.py
   ```
   *Note: This will create a `faiss_index` folder containing your local vector store.*

3. **Start the Interactive RAG Agent**:
   Run the main application script to launch the interactive prompt:
   ```bash
   uv run main.py
   ```
   You can now ask questions about the contents of your PDFs! Type `quit` or `exit` to end the session.
