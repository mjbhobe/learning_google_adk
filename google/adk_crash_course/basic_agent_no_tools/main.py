import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from google.adk.sessions import InMemorySessionService

from agent import root_agent
from utils import run_agent_query


async def main():
    console = Console()
    session_service = InMemorySessionService()
    my_user_id = "adk_adventurer_001"

    query = ""
    while True:
        # a simple console based chat with Agent
        query = Prompt.ask(
            "[bright_yellow]Your question (or type 'exit' or press Enter to quit): [/bright_yellow]",
            default="exit",
        )
        # query = input()
        if query.strip().lower() == "exit":
            console.print("[bright_yellow]Goodbye![/bright_yellow]")
            break

        console.print(f"[green]🗣️ User Query:[/green] '{query}'")

        final_response = await run_agent_query(
            # greeting_agent,
            root_agent,
            query,
            session_service=session_service,
            user_id=my_user_id,
        )
        console.print("[green]\n" + "-" * 50 + "[/green]")
        console.print("[green]✅ Agent Response:[/green]")
        console.print(Markdown(final_response))
        console.print("[green]\n" + "-" * 50 + "[/green]")


if __name__ == "__main__":
    asyncio.run(main())
