from dotenv import load_dotenv, find_dotenv

from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .tools import get_weather, get_current_time

load_dotenv(find_dotenv(), override=True)


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-3.1-flash-lite",
    description=(
        "An agent that answers questions about "
        "the weather and current time in cities."
    ),
    instruction=(
        "You are a helpful, friendly assistant that answers questions about "
        "weather and time in cities. Always be concise. If you don't have "
        "data for a city, say so clearly and apologise briefly."
    ),
    tools=[get_weather, get_current_time],
)
