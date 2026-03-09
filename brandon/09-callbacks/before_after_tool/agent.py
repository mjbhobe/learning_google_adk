"""
before_after_tool.py - illustrates ADK callbacks before & after
    tools are called

Code shared for learning purposes only! Use at own risk.
"""

import copy
from typing import Optional, Dict, Any
from rich.console import Console
from dotenv import load_dotenv
import logging

from google.adk.agents import Agent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Silence Pydantic's internal validation warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)

# 2. Silence LiteLLM's verbose logs (often the biggest culprit)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# 3. Silence ADK's model integration logs
# Note: Use 'google_adk' for the broad package or be specific as below
logging.getLogger("google_adk.models.lite_llm").setLevel(logging.WARNING)


AGENT_NAME = "simple_chatbot"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

load_dotenv()
console = Console()

openai_model = LiteLlm(model="openai/gpt-4o")


# --- Define a Simple Tool Function ---
def get_capital_city(country: str) -> Dict[str, str]:
    """
    Retrieves the capital city of a given country.

    Args:
        country: Name of the country

    Returns:
        Dictionary with the capital city result
    """
    print(f"[TOOL] Executing get_capital_city tool with country: {country}")

    country_capitals = {
        "united states": "Washington, D.C.",
        # "usa": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "germany": "Berlin",
        "japan": "Tokyo",
        "brazil": "Brasília",
        "australia": "Canberra",
        "india": "New Delhi",
        # "bharat": "New Delhi",
    }

    # Use lowercase for comparison
    result = country_capitals.get(country.lower(), f"Capital not found for {country}")
    console.print(f"[green][TOOL] Result: {result}[/green]")
    console.print(f"[green][TOOL] Returning: {{'result': '{result}'}}[/green]")

    return {"result": result}


# --- Define Before Tool Callback ---
def before_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    Simple callback that modifies tool arguments or skips the tool call.
    """
    tool_name = tool.name
    console.print(f"[yellow][Callback] Before tool call for '{tool_name}'[/yellow]")
    console.print(f"[yellow][Callback] Original args: {args}[/yellow]")

    # If someone asks about 'Merica, convert to United States
    # if tool_name == "get_capital_city" and args.get("country", "").lower() == "merica":
    if tool_name == "get_capital_city":
        if args.get("country", "").lower() in ["merica", "us", "usa"]:
            console.print(
                "[yellow][Callback] Converting 'Merica to 'United States'[/yellow]"
            )
            args["country"] = "United States"
            print(f"[Callback] Modified args: {args}")
        elif args.get("country", "").lower() in ["bharat"]:
            console.print("[yellow][Callback] Converting 'Bharat' to 'India'[/yellow]")
            args["country"] = "India"
            print(f"[Callback] Modified args: {args}")
        return None

    # Skip the call completely for restricted countries
    if (
        tool_name == "get_capital_city"
        and args.get("country", "").lower() == "restricted"
    ):
        console.print("[red][Callback] Blocking restricted country[/red]")
        return {"result": "Access to this information has been restricted."}

    console.print("[green][Callback] Proceeding with normal tool call[/green]")
    return None


# --- Define After Tool Callback ---
def after_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """
    Simple callback that modifies the tool response after execution.
    """
    tool_name = tool.name
    console.print(f"[yellow][Callback] After tool call for '{tool_name}'[/yellow]")
    console.print(f"[yellow][Callback] Args used: {args}[/yellow]")
    console.print(f"[yellow][Callback] Original response: {tool_response}[/yellow]")

    original_result = tool_response.get("result", "")
    console.print(f"[yellow][Callback] Extracted result: '{original_result}'[/yellow]")

    # Add a note for any USA capital responses
    if tool_name == "get_capital_city":
        if "washington" in original_result.lower():
            console.print(
                "[blue][Callback] DETECTED USA CAPITAL - adding patriotic note![/blue]"
            )

            # Create a modified copy of the response
            modified_response = copy.deepcopy(tool_response)
            modified_response["result"] = (
                f"{original_result} (Note: This is the capital of the USA. 🇺🇸)"
            )
            modified_response["note_added_by_callback"] = True
            return modified_response
        elif "delhi" in original_result.lower():
            console.print(
                "[orange][Callback] DETECTED USA CAPITAL - adding patriotic note![/orange]"
            )

            # Create a modified copy of the response
            modified_response = copy.deepcopy(tool_response)
            modified_response["result"] = (
                f"{original_result} (Note: This is India! Mera Bharat Mahaan!!! 🇮🇳)"
            )
            modified_response["note_added_by_callback"] = True
            console.print(
                f"[blue][Callback] Modified response: {modified_response}[/blue]"
            )
            return modified_response

    console.print(
        "[green][Callback] No modifications needed, returning original response[/green]"
    )
    return None


root_agent = Agent(
    name="tool_callback_agent",
    model=openai_model,
    description="An agent that demonstrates tool callbacks by looking up capital cities",
    instruction="""
    You are a helpful geography assistant.
    
    Your job is to:
    - Find capital cities when asked using the get_capital_city tool
    - Use the exact country name provided by the user
    - ALWAYS return the EXACT result from the tool, without changing it
    - When reporting a capital, display it EXACTLY as returned by the tool
    
    Examples:
    - "What is the capital of France?" → Use get_capital_city with country="France"
    - "Tell me the capital city of Japan" → Use get_capital_city with country="Japan"
    """,
    tools=[get_capital_city],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)
