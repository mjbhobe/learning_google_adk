import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService

from tools import get_weather, say_hello, say_goodbye
from utils import load_agent_config, run_agent_query
from logger import get_logger


# load API keys
load_dotenv(override=True)
console = Console()
logger = get_logger("agent_team.agents")

weather_agent_config = load_agent_config("weather_agent")
logger.info(
    f"Loaded weather_agent_config:\n   model -> {weather_agent_config['model']}"
    f"\n   description -> {weather_agent_config['description']}"
    f"\n   instruction -> {weather_agent_config['instruction']}"
)
greeting_agent_config = load_agent_config("greeting_agent")
farewell_agent_config = load_agent_config("farewell_agent")


# NOTE: ensure you have an entry for OPENAI_API_KEY in your .env file!
# also add google-adk[extensions] to your local Python environment
openai_model = LiteLlm(model="openai/gpt-4o")

weather_agent = LlmAgent(
    name="weather_agent",
    model=openai_model,
    # model=weather_agent_config["model"],
    description=weather_agent_config["description"],
    instruction=weather_agent_config["instruction"],
    tools=[get_weather],
)

# ----- greeting_agent ------
greeting_agent = LlmAgent(
    name="greeting_agent",
    model=openai_model,
    # model=greeting_agent_config["model"],
    description=greeting_agent_config["description"],
    instruction=greeting_agent_config["instruction"],
    tools=[say_hello],
)

# ----- farewell_agent ------
farewell_agent = LlmAgent(
    name="farewell_agent",
    model=openai_model,
    # model=farewell_agent_config["model"],
    description=farewell_agent_config["description"],
    instruction=farewell_agent_config["instruction"],
    tools=[say_goodbye],
)

# ----- weather agent team - uses greeting_agent & farewell_agent as sub-agents/tools -----
weather_agent_team = LlmAgent(
    name="weather_agent",
    model=openai_model,
    # model=weather_agent_config["model"],
    description=weather_agent_config["description"],
    instruction=weather_agent_config["instruction"],
    tools=[get_weather],
    # Key change: Link the sub-agents here!
    sub_agents=[greeting_agent, farewell_agent],
)


async def main():
    session_service = InMemorySessionService()
    session_id = "multi_agent_with_adk_demo_session_007"
    my_user_id = "adk_adventurer_001"
    # add some initial settings
    session_state = {
        "user_pref_temperature_units": "Celcius",
    }

    # if you want the agent to remember conversation context across calls
    # then create a session (outside of all calls to run_agent_query) and pass
    # that session object in each call to run_agent_query
    my_session = await session_service.create_session(
        app_name=weather_agent_team.name,
        user_id=my_user_id,
        session_id=session_id,
        state=session_state,
    )
    logger.info(f"Session created with ID: {session_id}")

    # test if I can retrieve the info
    retrieved_session = await session_service.get_session(
        app_name=weather_agent_team.name,
        user_id=my_user_id,
        session_id=session_id,
    )
    logger.info(
        f"Retrived session: {retrieved_session}\n"
        f"Retrieved state: {retrieved_session.state}"
    )

    query = ""
    while True:
        query = Prompt.ask(
            "[bright_yellow]Query (or type 'exit' or press Enter to quit): [/bright_yellow]",
            default="exit",
        )

        if query.strip().lower() == "exit":
            console.print("[bright_yellow]Goodbye![/bright_yellow]")
            logger.info("User exited the application.")
            break

        logger.info(f"🗣️ User Query: '{query}'")
        final_response = await run_agent_query(
            weather_agent_team,
            query,
            session_service,
            session=my_session,  # <-- pass the session here to maintain context across queries
            user_id=my_user_id,
            show_trace=False,
        )

        logger.info(f"Agent final response: {Markdown(final_response)}")
        console.print("[green]\n" + "-" * 50 + "\n[/green]")
        console.print("[green]✅ Final Response:[/green]")
        console.print(Markdown(final_response))
        console.print("[green]\n" + "-" * 50 + "\n[/green]")


if __name__ == "__main__":
    asyncio.run(main())
