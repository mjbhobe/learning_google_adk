import asyncio
import os
import pathlib
from dotenv import load_dotenv
from rich.console import Console

from google.adk.runners import Runner
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part

from rag_pipeline import build_local_index
from local_rag_agent.agent import local_rag_agent

load_dotenv(override=True)
assert os.getenv(
    "OPENAI_API_KEY"
), f"FATAL ERROR: {pathlib.Path(__file__).name} -> OPENAI_API_KEY not defined!"

FAISS_INDEX_PATH = pathlib.Path(__file__).parent / "faiss_index"

APP_NAME = "local_rag_app"
USER_ID = "adk_user_007"

console = Console()

async def run_agent_query(
    agent: Agent,
    query: str,
    session_service: InMemorySessionService,
    session: Session = None,
    user_id: str = USER_ID,
) -> str:

    console.print(f"[blue]🗣️ User Query: '{query}'[/blue]")

    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name=APP_NAME,
    )

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=Content(parts=[Part(text=query)], role="user"),
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                else:
                    # Handle cases like UNEXPECTED_TOOL_CALL or empty turns
                    final_response = f"Agent finished with reason: {getattr(event, 'finish_reason', 'Unknown')}"
                    if hasattr(event, "error_message") and event.error_message:
                        final_response += f" - {event.error_message}"
    except Exception as e:
        final_response = f"An error occurred: {e}"

    return final_response


async def main():

    # 1. build faiss index, if it does not exist
    if not FAISS_INDEX_PATH.exists():
        pdf_path = pathlib.Path(__file__).parent / "docs"
        build_local_index(str(pdf_path))

    session_service = InMemorySessionService()
    session: Session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    # console = Console()

    console.print("[yellow]Welcome to LOCAL RAG Agent[/yellow]")
    console.print("[yellow]Enter your query or type exit or quit to exit[/yellow]")

    user_query = ""
    while True:
        console.print("[green]Query? [/green]", end="")
        user_query = input().strip()

        if user_query.lower() in ["quit", "exit"]:
            break
        else:
            response: str = await run_agent_query(
                local_rag_agent,
                user_query,
                session_service,
                session,
            )
            # user_query = "What are the key findings in the documents?"
            console.print(f"\n🤖 Agent Response:\n{response}")


if __name__ == "__main__":
    asyncio.run(main())
