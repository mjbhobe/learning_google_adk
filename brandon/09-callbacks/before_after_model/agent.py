"""
before_after_model.py - illustrates callbacks before & after LLM (model)
    is called

Code shared for learning purposes only! Use at own risk.
"""
import copy
from datetime import datetime
from typing import Optional
from rich.console import Console
from dotenv import load_dotenv
import logging

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
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


def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    This callback runs before the model processes a request.
    Such callbacks can be used to filter inappropriate content
    and logs request info.

    In this example, we check if the user query contains the word
    "sucks" - if so we block the request.

    Args:
        callback_context: Contains state and context information
        llm_request: The LLM request being sent

    Returns:
        None: signalling all-good and proceed with normal model request
        ELSE an instance of LlmResponse to stop normal workflow
            In this example we return this when user request contains word "sucks"
    """
    # Get the state and agent name
    state = callback_context.state
    agent_name = callback_context.agent_name

    # Extract the last user message
    last_user_message = ""
    if llm_request.contents and len(llm_request.contents) > 0:
        # we want to inspect the latest (last) user request, hence "reversed"
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts and len(content.parts) > 0:
                if hasattr(content.parts[0], "text") and content.parts[0].text:
                    last_user_message = content.parts[0].text
                    break

    # Log the request
    console.print("[yellow]=== MODEL REQUEST STARTED ===[/yellow]")
    console.print(f"[yellow]Agent: {agent_name} [/yellow]")
    if last_user_message:
        console.print(f"[yellow]User message: {last_user_message[:100]}...[/yellow]")
        # Store for later use
        state["last_user_message"] = last_user_message
    else:
        print("User message: <empty>")

    console.print(f"Timestamp: {datetime.now().strftime(DATETIME_FORMAT)}")

    # Check for inappropriate content
    if last_user_message and "sucks" in last_user_message.lower():
        console.print("[red]=== INAPPROPRIATE CONTENT BLOCKED ===[/red]")
        console.print("[red]Blocked text containing prohibited word: 'sucks'[/red]")

        console.print(
            "[red][BEFORE MODEL] ⚠️ Request blocked due to inappropriate content[/red]"
        )

        # Return a response to skip the model call
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text="I cannot respond to messages containing inappropriate language. "
                        "Please rephrase your request WITHOUT using words like 'sucks'."
                    )
                ],
            )
        )

    # Record start time for duration calculation
    state["model_start_time"] = datetime.now().strftime(DATETIME_FORMAT)
    console.print("[green][BEFORE MODEL] ✓ Request approved for processing[/green]")

    # Return None to proceed with normal model request
    return None


def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    Simple callback that replaces negative words with more positive alternatives.

    Args:
        callback_context: Contains state and context information
        llm_response: The LLM response received

    Returns:
        Optional LlmResponse to override model response
    """
    # Log completion
    console.print("[green][AFTER MODEL] Processing response[/green]")

    # Skip processing if response is empty or has no text content
    if not llm_response or not llm_response.content or not llm_response.content.parts:
        return None

    # Extract text from the response
    response_text = ""
    for part in llm_response.content.parts:
        if hasattr(part, "text") and part.text:
            response_text += part.text

    if not response_text:
        return None

    # Simple word replacements
    replacements = {
        "problem": "challenge",
        "difficult": "complex",
    }

    # Perform replacements
    modified_text = response_text
    modified = False

    for original, replacement in replacements.items():
        if original in modified_text.lower():
            modified_text = modified_text.replace(original, replacement)
            modified_text = modified_text.replace(
                original.capitalize(), replacement.capitalize()
            )
            modified = True

    # Return modified response if changes were made
    if modified:
        console.print("[green][AFTER MODEL] ↺ Modified response text[/green]")

        modified_parts = [copy.deepcopy(part) for part in llm_response.content.parts]
        for i, part in enumerate(modified_parts):
            if hasattr(part, "text") and part.text:
                modified_parts[i].text = modified_text

        return LlmResponse(content=types.Content(role="model", parts=modified_parts))

    # Return None to use the original response
    return None


root_agent = Agent(
    name="content_filter_agent",
    model=openai_model,
    description="An agent that demonstrates model callbacks for content filtering and logging",
    instruction="""
    You are a helpful assistant.
    
    Your job is to:
    - Answer user questions concisely
    - Provide factual information
    - Be friendly and respectful
    """,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
