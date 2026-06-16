"""
utils.py - utility functions
"""

import os
import sys
import json
import contextlib
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

if sys.platform == "win32":
    import msvcrt
else:
    import termios
    import tty


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

    # Create a new, single-use session for this query ONLY if caller
    # doesn't pass a valid session object.
    # NOTE: a Session is ALWAYS required by the agent to run a user query
    # If you do not pass in a session object, the following line will create 
    # a session which will "dissappear" after the run_agent_query() call.
    # So, if you want to maintain a "history" of the conversation, pass in a valid 
    # session object to this function.
    my_session: Session = session or await session_service.create_session(
        app_name=agent.name, user_id=user_id
    )

    # console.print(f"[blue]🗣️ User Query: '{query}'[/blue]")

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

    # if not is_router:
    #     console.print("[green]\n" + "-" * 50 + "\n[/green]")
    #     console.print("[green]✅ Final Response:[/green]")
    #     console.print(Markdown(final_response))
    #     console.print("[green]\n" + "-" * 50 + "\n[/green]")

    return final_response


def load_cache(cache_file_path: str) -> list[dict]:
    """Load a query/response cache from disk, if it exists."""
    if os.path.exists(cache_file_path):
        try:
            with open(cache_file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError, OSError:
            return []
    return []


def save_cache(cache: list[dict], cache_file_path: str) -> None:
    """Persist a query/response cache to disk."""
    with open(cache_file_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


@contextlib.contextmanager
def _raw_terminal():
    """Put the terminal into raw (unbuffered, unechoed) mode for the duration of the block.
    No-op on Windows, where msvcrt.getch() already reads unbuffered/unechoed."""
    if sys.platform == "win32":
        yield
        return
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _read_key() -> str | None:
    """Read a single keypress and normalize it to 'ENTER', 'BACKSPACE', 'DELETE',
    'UP', 'DOWN', 'LEFT', 'RIGHT', 'HOME', 'END', a single printable character,
    or None if the key should be ignored."""
    if sys.platform == "win32":
        ch = msvcrt.getch()
        if ch in (b"\r", b"\n"):
            return "ENTER"
        if ch == b"\x08":
            return "BACKSPACE"
        if ch in (b"\xe0", b"\x00"):  # prefix byte for arrow/function keys
            ch2 = msvcrt.getch().decode("ascii", "ignore")
            return {
                "H": "UP",
                "P": "DOWN",
                "K": "LEFT",
                "M": "RIGHT",
                "S": "DELETE",
                "G": "HOME",
                "O": "END",
            }.get(ch2)
        try:
            return ch.decode("utf-8")
        except UnicodeDecodeError:
            return None
    else:
        ch = sys.stdin.read(1)
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch in ("\x7f", "\x08"):
            return "BACKSPACE"
        if ch == "\x1b":  # ESC introduces an arrow/function key sequence
            if sys.stdin.read(1) != "[":
                return None
            code = sys.stdin.read(1)
            simple = {
                "A": "UP",
                "B": "DOWN",
                "C": "RIGHT",
                "D": "LEFT",
                "H": "HOME",
                "F": "END",
            }
            if code in simple:
                return simple[code]
            if code.isdigit():
                num = code
                while True:
                    c2 = sys.stdin.read(1)
                    if c2 == "~":
                        break
                    num += c2
                return {
                    "3": "DELETE",
                    "1": "HOME",
                    "7": "HOME",
                    "4": "END",
                    "8": "END",
                }.get(num)
            return None
        return ch


def _redraw_line(prompt_label: str, buffer: str, cursor: int) -> None:
    """Clear the current console line and redraw it with the given buffer,
    placing the terminal cursor at the given position within the buffer."""
    sys.stdout.write("\r" + " " * (len(prompt_label) + len(buffer) + 20) + "\r")
    sys.stdout.write(f"\033[93m{prompt_label}\033[0m{buffer}")
    move_left = len(buffer) - cursor
    if move_left > 0:
        sys.stdout.write(f"\033[{move_left}D")
    sys.stdout.flush()


def ask_user_query(cache: list[dict], prompt_label: str) -> str:
    """
    Prompt the user for input on the console, supporting Up/Down arrow
    navigation through previously entered queries stored in `cache`.

    Up arrow: step backwards from the most recent cached query towards the
    oldest, stopping at the oldest.
    Down arrow: step forwards towards the most recent cached query, then to
    a blank line once past the most recent.

    Args:
        cache: list of {"query": ..., "response": ...} dicts, oldest first.
        prompt_label: text to display before the user's input.

    Returns the text entered by the user (or "exit" on a blank Enter).
    """
    queries = [entry["query"] for entry in cache]
    history_pos = len(queries)  # one past the last entry == blank line
    buffer = ""
    cursor = 0

    sys.stdout.write(f"\033[93m{prompt_label}\033[0m")
    sys.stdout.flush()

    with _raw_terminal():
        while True:
            key = _read_key()

            if key is None:
                continue

            if key == "ENTER":
                sys.stdout.write("\r\n")
                sys.stdout.flush()
                return buffer if buffer else "exit"

            elif key == "\x03":  # Ctrl+C
                sys.stdout.write("\r\n")
                sys.stdout.flush()
                raise KeyboardInterrupt

            elif key == "BACKSPACE":
                if cursor > 0:
                    buffer = buffer[: cursor - 1] + buffer[cursor:]
                    cursor -= 1
                    _redraw_line(prompt_label, buffer, cursor)

            elif key == "DELETE":
                if cursor < len(buffer):
                    buffer = buffer[:cursor] + buffer[cursor + 1 :]
                    _redraw_line(prompt_label, buffer, cursor)

            elif key == "LEFT":
                if cursor > 0:
                    cursor -= 1
                    sys.stdout.write("\033[1D")
                    sys.stdout.flush()

            elif key == "RIGHT":
                if cursor < len(buffer):
                    cursor += 1
                    sys.stdout.write("\033[1C")
                    sys.stdout.flush()

            elif key == "HOME":
                if cursor != 0:
                    cursor = 0
                    _redraw_line(prompt_label, buffer, cursor)

            elif key == "END":
                if cursor != len(buffer):
                    cursor = len(buffer)
                    _redraw_line(prompt_label, buffer, cursor)

            elif key == "UP":
                if queries and history_pos > 0:
                    history_pos -= 1
                    buffer = queries[history_pos]
                    cursor = len(buffer)
                    _redraw_line(prompt_label, buffer, cursor)

            elif key == "DOWN":
                if history_pos < len(queries) - 1:
                    history_pos += 1
                    buffer = queries[history_pos]
                    cursor = len(buffer)
                    _redraw_line(prompt_label, buffer, cursor)
                elif history_pos == len(queries) - 1:
                    history_pos = len(queries)
                    buffer = ""
                    cursor = 0
                    _redraw_line(prompt_label, buffer, cursor)

            elif len(key) == 1 and key.isprintable():
                buffer = buffer[:cursor] + key + buffer[cursor:]
                cursor += 1
                _redraw_line(prompt_label, buffer, cursor)
            # other special keys are ignored
