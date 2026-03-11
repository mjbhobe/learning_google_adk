import asyncio
import os
import pathlib
from dotenv import load_dotenv
from rich.console import Console

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from rag_pipeline import build_local_index
from agent import local_rag_agent

load_dotenv(override=True)
assert os.getenv(
    "OPENAI_API_KEY"
), f"FATAL ERROR: {pathlib.Path(__file__).name}: OPENAI_API_KEY not defined!"

FAISS_INDEX_PATH = pathlib.Path(__file__).parent / "faiss_index"


async def main():

    # 1. build faiss index, if it does not exist
    if not FAISS_INDEX_PATH.exists():
        pdf_path = pathlib.Path(__file__).parent / "docs"
        build_local_index(str(pdf_path))

    session_service = InMemorySessionService()
    runner = Runner(agent=local_rag_agent, session_service=session_service)
    console = Console()

    console.print("[yellow]Welcome to LOCAL RAG Agent[/yellow]")
    console.print("[yellow]Enter your query or type exit or quit to exit[/yellow]")

    user_query = ""
    while True:
        console.print("[green]Query? [/green]", end="")
        user_query = input().strip()

        if user_query.lower() in ["quit", "exit"]:
            break
        else:
            # user_query = "What are the key findings in the documents?"
            async for event in runner.run_async(
                user_id="local_rag_user", input=user_query
            ):
                if event.is_final():
                    print(f"\n🤖 OpenAI Agent Response:\n{event.content}")


if __name__ == "__main__":
    asyncio.run(main())
