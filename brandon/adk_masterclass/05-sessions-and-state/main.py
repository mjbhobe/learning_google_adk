import asyncio
import uuid
from dotenv import load_dotenv

from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai import types

from manu_bot.agent import root_agent
from manu_bot.logger import get_logger


load_dotenv(override=True)
logger = get_logger("sessions_and_memory.main")


async def main():

    console = Console()

    session_service = InMemorySessionService()

    app_name = Path(__file__).parent.resolve().name
    user_id = "adk_adventurer_007"
    session_id = str(uuid.uuid4())

    # let's create a session with some initial_state, which the agent
    # will use for answering questions about me
    initial_state = {
        "user_name": "Manish Bhobe",
        "user_preferences": """
        I am from India. 
        My favourite holiday destinations are Goa, Singapore and Spain.
        I like to play cricket and football.
        My favourite cricket team is, of course, India followed closely by Australia.
        My favourite IPL team is Mumbai Indians and RCB.
        My favourite football club is Chelsea FC followed closely by Barcelona
        My favourite football teams are Argentina, France and Spain.
        My favorite food is Lebanese - I adore kababs & gyros.
        My favorite TV show is Breaking Bad.
        I love to program Python and get into deep discussions around Agentic AI.
        My favourite Agentic AI Frameworks are Google ADK, LangChain and LangGraph
    """,
    }

    my_session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=initial_state,
    )

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=app_name,
    )

    query = ""
    while True:
        console.print(
            "\n[bold blue] What do you want to know about me? (or 'exit' if you've had enough!): [/bold blue]",
            end="",
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
