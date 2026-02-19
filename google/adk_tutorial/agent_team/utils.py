"""
utils.py - utility functions
"""

import os
import asyncio
import yaml
import httpx
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part
from google.adk.agents import Agent

from logger import get_logger


CONFIG_PATH = Path(__file__).parent / "agents_config.yaml"
console = Console()
logger = get_logger("agent_team.utils")


def load_agent_config(agent_name: str, config_path: Path = CONFIG_PATH):
    """
    loads agent config from YAML file

    Args:
        agent_name (str): name of the agent
        config_path (Path, optional): path to the config file. Defaults to CONFIG_PATH.
    """
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config.get(agent_name)


async def run_agent_query(
    agent: Agent,
    query: str,
    session_service: InMemorySessionService,
    session: Session = None,
    user_id: str = "adk_developer_007",
    is_router: bool = False,
    show_trace: bool = False,
) -> str:
    # Create a new, single-use session for this query ONLY if caller
    # doesn't pass a valid session object.
    logger.debug(
        f"run_agent_query called with:"
        f"\n   agent name: {agent.name}"
        f"\n   user_id: {user_id}"
        f"\n   query: {query}"
        f"\n   session_service passed: {'Yes' if session_service else 'No'}"
        f"\n   session passed: {'Yes' if session else 'No'}"
        f"\n   session_id: {session.id if session else 'None'}"
        f"\n   is_router: {is_router}"
    )

    my_session: Session = session or await session_service.create_session(
        app_name=agent.name, user_id=user_id
    )

    # console.print(f"[blue]🗣️ User Query: '{query}'[/blue]")

    """Initializes a runner and executes a query for a given agent and session."""
    # console.print(
    #     f"[green]\n🚀 Running query for agent: '{agent.name}' in session: '{my_session.id}'...[/green]"
    # )

    runner = Runner(agent=agent, session_service=session_service, app_name=agent.name)

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=my_session.id,
            new_message=Content(parts=[Part(text=query)], role="user"),
        ):
            if (not is_router) and (show_trace):
                # Let's see what the agent is thinking!
                logger.info(f"EVENT: {event}")
            if event.is_final_response():
                # FIX suggested by Google Gemini
                # Check if event has content and parts before accessing
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                else:
                    # Handle cases like UNEXPECTED_TOOL_CALL or empty turns
                    final_response = f"Agent finished with reason: {getattr(event, 'finish_reason', 'Unknown')}"
                    if hasattr(event, "error_message") and event.error_message:
                        final_response += f" - {event.error_message}"
                # final_response = event.content.parts[0].text
    except Exception as e:
        final_response = f"An error occurred: {e}"

    # if not is_router:
    #     console.print("[green]\n" + "-" * 50 + "\n[/green]")
    #     console.print("[green]✅ Final Response:[/green]")
    #     console.print(Markdown(final_response))
    #     console.print("[green]\n" + "-" * 50 + "\n[/green]")

    return final_response
