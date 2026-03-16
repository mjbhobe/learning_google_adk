import os
from dotenv import load_dotenv
import textwrap
from datetime import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


from .tools import get_current_time, get_live_weather_global

load_dotenv(override=True)
assert os.getenv("ANTHROPIC_API_KEY") is not None, "FATAL: ANTHROPIC_API_KEY is not set"


PROMPT = """
You are a helpful assistant that answers user's questions about weather & time in a city.
You have access to the following tools:
- get_current_time: Use this tool to get the current time in a city.
- get_live_weather_global: Use this tool to get the live weather in a city.
ALWAYS use the tools to find information & do not answer from your 
pretrained data even if you know the answer!
For questions not related to weather or time, respond with a polite error message.
"""

root_agent = LlmAgent(
    name="agent_with_functional_tools",
    model="gemini-2.5-flash",  # LiteLlm(model="anthropic/claude-sonnet-4-6"),
    # description="A helpful agent that answers user's questions about time & weather",
    instruction=textwrap.dedent(PROMPT).strip(),
    tools=[get_current_time, get_live_weather_global],
)
