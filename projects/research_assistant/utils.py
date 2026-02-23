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
    console.print(f"[cyan]🔍 Calling web_search with query: '{query}'[/cyan]")

    api_key = os.environ.get("TAVILY_API_KEY")

    if not api_key:
        return "Error: TAVILY_API_KEY is not set in environment variables."

    # Tavily requires a specific JSON payload and Header
    url = "https://api.tavily.com/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": query[:400],  # Enforce the 400 char limit
        "search_depth": "basic",
        "max_results": 5,
    }

    async with httpx.AsyncClient() as client:
        try:
            # We use json=payload to ensure httpx serializes it correctly
            response = await client.post(
                url, headers=headers, json=payload, timeout=10.0
            )

            if response.status_code != 200:
                return f"Tavily API Error {response.status_code}: {response.text}"

            data = response.json()
            results = data.get("results", [])

            if not results:
                return "No search results found for this query."

            output = []
            for r in results:
                output.append(
                    f"Title: {r.get('title')}\nSource: {r.get('url')}\nContent: {r.get('content')}"
                )

            return "\n\n---\n\n".join(output)

        except Exception as e:
            return f"An unexpected error occurred during search: {str(e)}"


async def run_agent_query(
    agent: Agent,
    query: str,
    session_service: InMemorySessionService,
    session: Session = None,
    user_id: str = "adk_developer_007",
    is_router: bool = False,
    show_trace: bool = False,
) -> str:
    """ utility function to run an agent 
    Args:
        agent (Agent) - the agent you want to run
        query (str) - the query (prompt) you want this agent to run
        session_service (InMemorySessionservice) - the session service running the agent
        session (Session; optional, default=None) - pass in an instance of a session ONLY if you want this
            agent to track chat-history. Else this function creates a session to run query.
        user_id (str; optional, default='adk_developer_007') - optional user_id for session
        is_router (bool; optional default=False): pass True if this is a Router Agent
        show_trace (bool; optional, default=False): pass in True if you want to see intermediate Agent output
            (works when is_router is False)
    """

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

    runner = Runner(
        agent=agent,
        session_service=session_service,
        # app_name=agent.name,
        app_name=my_session.app_name,
    )

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=my_session.id,
            new_message=Content(parts=[Part(text=query)], role="user"),
        ):
            if (not is_router) and (show_trace):
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


    return final_response

