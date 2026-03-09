from datetime import datetime
from typing import Optional
from rich.console import Console
from dotenv import load_dotenv
import logging

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
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


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Simple callback that logs when the agent starts processing a request.

    Args:
        callback_context: Contains state and context information

    Returns:
        None to continue with normal agent processing
    """
    # grab the state
    state = callback_context.state

    timestamp = datetime.now()

    # ---- you can modify state like this -----------
    if "agent_name" not in state:
        state["agent_name"] = AGENT_NAME

    # initialize request counter to track # of requests to this agent
    if "request_counter" not in state:
        state["request_counter"] = 1
    else:
        state["request_counter"] += 1

    state["request_start_time"] = timestamp.strftime(DATETIME_FORMAT)

    # ------ add your logs ------------------
    console.print("[bright_yellow]=== AGENT EXECUTION STARTED ===[/bright_yellow]")
    console.print(f"[yellow]Request #: {state['request_counter']}   [/yellow]")
    console.print(f"[yellow]Timestamp: {timestamp.strftime(DATETIME_FORMAT)}[/yellow]")

    # Print to console
    print(f"\n[BEFORE CALLBACK] Agent processing request #{state['request_counter']}")

    return None


def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Simple callback that logs when the agent finishes processing a request.

    Args:
        callback_context: Contains state and context information

    Returns:
        None to continue with normal agent processing
    """
    # Get the session state
    state = callback_context.state

    # Calculate request duration if start time is available
    timestamp = datetime.now()
    duration = None
    if "request_start_time" in state:
        start_time = datetime.strptime(state["request_start_time"], DATETIME_FORMAT)
        duration = (timestamp - start_time).total_seconds()

    # Log the completion
    console.print("[bright_yellow]=== AGENT EXECUTION COMPLETED ===[/bright_yellow]")
    console.print(
        f"[yellow]Request #: {state.get('request_counter', 'Unknown')}[/yellow]"
    )
    if duration is not None:
        console.print(f"[yellow]Duration: {duration:.2f} seconds[/yellow]")

    # Print to console
    console.print(
        f"[yellow][AFTER CALLBACK] Agent completed request #{state.get('request_counter', 'Unknown')}[/yellow]"
    )
    if duration is not None:
        console.print(f"[yellow]Processing took {duration:.2f} seconds[/yellow]")

    return None


root_agent = Agent(
    name="before_after_agent",
    model=openai_model,
    description="A basic agent that demonstrates before and after agent callbacks",
    # we initialized agent_name in the state in the before_agent_callback call
    # we can now use it in the Agent like below {agent_name}
    instruction="""
    You are a friendly greeting agent. Your name is {agent_name}.
    
    Your job is to:
    - Greet users politely
    - Respond to basic questions
    - Keep your responses friendly and concise
    """,
    before_agent_callback=[before_agent_callback],
    after_agent_callback=[after_agent_callback],
)
