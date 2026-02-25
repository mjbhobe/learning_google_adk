import asyncio
from dotenv import load_dotenv

from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai import types

from agent import root_agent
from logger import get_logger


load_dotenv(override=True)
logger = get_logger("tool_agent.main")


async def main():

    console = Console()

    session_service = InMemorySessionService()

    app_name = Path(__file__).parent.resolve().name
    user_id = "adk_adventurer_007"

    my_session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
    )

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=app_name,
    )

    query = ""
    while True:
        console.print(
            "\n[bold blue]Enter your query (or 'exit' to quit):[/bold blue]", end=" "
        )
        query = input().strip()

        if query.lower() == "exit":
            console.print("[bold red]Exiting... Goodbye![/bold red]")
            break
        else:
            # Process the query using the ADK runner
            logger.info(f"Processing user query: [yellow]{query}[/yellow]")

            # 3. Format the input for the ADK Runner
            user_content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=query)],
            )

            # 4. Execute using the runner
            # Note: InMemoryRunner.run returns a generator of events
            async for event in runner.run_async(
                user_id=user_id,
                session_id=my_session.id,
                new_message=user_content,
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        # The final response is usually the last text part
                        console.print("\n[bold green]Agent Response:[/bold green]")
                        console.print(Markdown(event.content.parts[0].text))


if __name__ == "__main__":
    asyncio.run(main())
