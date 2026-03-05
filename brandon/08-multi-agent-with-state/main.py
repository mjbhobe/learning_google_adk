import asyncio
from dotenv import load_dotenv
from rich.console import Console

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

from logger import get_logger
from customer_service_agent.agent import customer_service_agent
from utils import add_user_query_to_history, call_agent_async

load_dotenv(override = True)
console = Console()
logger = get_logger("customer_service_agent.main")

# define some globals
APP_NAME = "customer_service_app"
USER_ID = "genaiwithmjb"

# define initial state for session
session_service = InMemorySessionService()
initial_state = {
    "user_name": "Manish Bhobe",
    "purchased_courses": [],
    "interaction_history": [],
}


async def main():
    # --- create the common session across agents ----------
    session = session_service.create_session(
        app_name = APP_NAME,
        user_id = USER_ID,
        state = initial_state,
    )
    SESSION_ID = session.id
    logger.info(f"Created session with id: {session.id}")

    # ----- create a runner to run the agents ---------------
    runner = Runner(
        agent = customer_service_agent,
        session_service = session_service,
        app_name = APP_NAME
    )

    console.print(f"[yellow]Welcome to Customer Service chat![/yellow]")
    console.print(f"[dark_yellow]Type exit or quit to end conversation[/dark_yellow]")

    while True:
        console.print("[light_green]You? [/light_green]", end = "")
        user_input = input().strip().lower()

        if user_input in ["exit", "quit"]:
            console.print("[red]Quitting...goodbye![/red]")
            break

        add_user_query_to_history(
            session_service,
            APP_NAME, USER_ID, SESSION_ID,
            user_input,
        )

        # Process the user query through the agent
        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

    # Dump Session at end of conversation
    final_session = session_service.get_session(
        app_name = APP_NAME, user_id = USER_ID, session_id = SESSION_ID
    )
    print("\nFinal Session State:")
    for key, value in final_session.state.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
