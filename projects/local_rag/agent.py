import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from tools import search_faiss

load_dotenv(override=True)
assert os.getenv(
    "OPENAI_API_KEY"
), f"FATAL ERROR: {pathlib.Path(__file__).name}: OPENAI_API_KEY not defined!"

model = LiteLlm(model="openai/gpt-4o")

local_rag_agent = LlmAgent(
    name="local_rag_agent",
    model=model,
    instruction="""
    You are a research assistant. 
    You have access to a FAISS vector store containing local PDFs.
    Always use 'search_faiss' to retrieve context before answering.
    """,
    tools=[search_faiss],
)
