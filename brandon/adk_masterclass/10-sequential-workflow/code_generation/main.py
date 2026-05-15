"""
Code Generation example using Sequential agents

This is the command line driver program that takes input from the
user, setups the session etc. & runs the main SequentialAgent
"""

import asyncio
import uuid
from dotenv import load_dotenv

from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai import types

# --- main driver agent ---
from code_pipeline_agent.agent import root_agent


async def main():

    console = Console()

    session_service = InMemorySessionService()

    app_name = Path(__file__).parent.resolve().name
    user_id = "adk_adventurer_007"
    session_id = str(uuid.uuid4())

    my_session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
    )

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=app_name,
    )

    requirements = ""
    while True:
        console.print(
            "\n[bold blue]Enter your requirements for code generation (or type exit to quit): [/bold blue]"
        )
        requirements = input().strip()

        if requirements.lower() == "exit":
            console.print("[bold red]Exiting... Goodbye![/bold red]")
            break
        else:
            # 3. Format the input for the ADK Runner
            user_content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=requirements)],
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
