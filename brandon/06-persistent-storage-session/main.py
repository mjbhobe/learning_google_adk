import asyncio
import uuid
from dotenv import load_dotenv

from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

from google.adk.sessions import DatabaseSessionService, Session
from google.adk.runners import Runner
from google.genai import types

from memory_agent.agent import root_agent
from memory_agent.logger import get_logger

APP_NAME = Path(__file__).parent.resolve().name

load_dotenv(override=True)
logger = get_logger(f"{APP_NAME}.main")

# our session will be persisted to this SQLite database
db_url = f"sqlite:///./{APP_NAME}_data.db"
session_service = DatabaseSessionService(db_url=db_url)

# will be used only the very first time session is created
initial_state = {
    "user_name": "Manish Bhobe",
    "reminders": [],
}


async def main():
    console = Console()

    app_name = APP_NAME
    user_id = "adk_adventurer_007"
    session_id = str(uuid.uuid4())

    # list all sessions available
    existing_sessions = await session_service.list_sessions(
        app_name=app_name,
        user_id=user_id,
    )

    # use existing session or create a new one
    if existing_sessions and len(existing_sessions.sessions) > 0:
        session_id = existing_sessions.sessions[0].id
        console.print(
            f"[sky_blue]Continuing to use existing session ID {session_id}[/sky_blue]"
        )
    else:
        console.print(f"[sky_blue]Creating new session[/sky_blue]")
        new_session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            initial_state=initial_state,
        )
        session_id = new_session.id
        console.print(f"[sky_blue]Created new session ID {session_id}[/sky_blue]")

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=app_name,
    )

    console.print(f"[dark_sea_green]Welcome to memory agent chat[/dark_sea_green]")

    query = ""
    while True:
        console.print(
            "\n[sky_blue]Your query? (or 'exit' to quit!)[/sky_blue]",
            end="",
        )
        query = input().strip()

        if query.lower() == "exit":
            console.print("[bold red]Exiting... Goodbye![/bold red]")
            break
        else:
            # Process the query using the ADK runner
            logger.info(f"Processing user query: {query}")

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
