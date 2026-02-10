"""
utils.py - utility functions
"""

import asyncio
import yaml
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part
from google.adk.agents import Agent


CONFIG_PATH = Path(__file__).parent / "agents_config.yaml"
console = Console()


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
    session_id: str,
    user_id: str,
    is_router: bool = False,
):
    """Initializes a runner and executes a query for a given agent and session."""
    console.print(
        f"[green]\n🚀 Running query for agent: '{agent.name}' in session: '{session_id}'...[/green]"
    )

    runner = Runner(agent=agent, session_service=session_service, app_name=agent.name)

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=Content(parts=[Part(text=query)], role="user"),
        ):
            if not is_router:
                # Let's see what the agent is thinking!
                console.print(f"[yellow]EVENT: {event}[/yellow]")
            if event.is_final_response():
                final_response = event.content.parts[0].text
    except Exception as e:
        final_response = f"An error occurred: {e}"

    if not is_router:
        console.print("[green]\n" + "-" * 50 + "\n[/green]")
        console.print("[green]✅ Final Response:[/green]")
        console.print(Markdown(final_response))
        console.print("[green]\n" + "-" * 50 + "\n[/green]")

    return final_response
