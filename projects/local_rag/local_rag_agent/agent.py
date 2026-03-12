import os
import pathlib
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .tools import search_faiss

load_dotenv(override=True)
assert os.getenv(
    "OPENAI_API_KEY"
), f"FATAL ERROR: {pathlib.Path(__file__).name} -> OPENAI_API_KEY not defined!"

model = LiteLlm(model="openai/gpt-4o")

local_rag_agent = LlmAgent(
    name="local_rag_agent",
    model=model,
    instruction="""
    You are a research assistant that ONLY answers questions using the local document store.

    RULES (follow strictly):
    1. For EVERY user question, you MUST call the 'search_faiss' tool first to retrieve context.
    2. BASE YOUR ANSWER EXCLUSIVELY on the text returned by 'search_faiss'.
       Do NOT use your pre-trained knowledge, even if you know the answer.
    3. If 'search_faiss' returns no relevant information, respond EXACTLY with:
       "I could not find relevant information in the available documents."
    4. When answering, ALWAYS cite the source document and page number provided in the
       search results using the format: **(Source: <filename>, Page: <page>)**.
    5. Format your response in Markdown for readability.
    6. At the end of your response, add a "References" section listing all sources used.
    """,
    tools=[search_faiss],
)
