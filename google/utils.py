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


async def web_search(query: str) -> str:
    """
    Performs a real-time web search to find the latest information.
    Use this for news, restaurant recommendations, or current events.
    This function uses Tavily search, so add TAVILY_API_KEY to your
    .env file to use it.

    NOTE: to be used as a web-search tool instead of google_search when using
    a non-Google LLM (such as OpenAI or Anthropic). ADK does not support using
    google tools (such as google_search) with a non-Google LLM, such as OpenAI

    Args:
        query: The search query string.
    """
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": os.environ.get("TAVILY_API_KEY"),
        "query": query,
        "search_depth": "smart",
    }

    # We use an async context manager for the client
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        results = response.json().get("results", [])

    formatted_results = [
        f"Source: {r['url']}\nContent: {r['content']}" for r in results
    ]
    return "\n\n".join(formatted_results)


async def run_agent_query(
    agent: Agent,
    query: str,
    session_service: InMemorySessionService,
    session: Session = None,
    user_id: str = "adk_developer_007",
    is_router: bool = False,
) -> str:
    # Create a new, single-use session for this query ONLY if caller
    # doesn't pass a valid session object.
    my_session: Session = session or await session_service.create_session(
        app_name=agent.name, user_id=user_id
    )

    console.print(f"[blue]🗣️ User Query: '{query}'[/blue]")

    """Initializes a runner and executes a query for a given agent and session."""
    console.print(
        f"[green]\n🚀 Running query for agent: '{agent.name}' in session: '{my_session.id}'...[/green]"
    )

    runner = Runner(agent=agent, session_service=session_service, app_name=agent.name)

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=my_session.id,
            new_message=Content(parts=[Part(text=query)], role="user"),
        ):
            if not is_router:
                # Let's see what the agent is thinking!
                console.print(f"[yellow]EVENT: {event}[/yellow]")
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
