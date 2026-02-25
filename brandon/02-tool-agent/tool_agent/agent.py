from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .tools import get_live_weather_global, web_search
from .logger import get_logger

load_dotenv(override=True)
# Initialize agent-level logger
logger = get_logger("tool_agent.agent")


openai_model = LiteLlm(model="openai/gpt-4o")

root_agent = Agent(
    name="tool_agent",
    model=openai_model,
    description="Agent that can use tools",
    instruction="""
    You are a helpful travel guide who can provide weather information.
    Use 'get_live_weather_global' to fetch weather information. For any other queries, use
    'google_search' tool to find relevant information. 
    Always provide a helpful response to the user.
    """,
    tools=[get_live_weather_global, web_search],
)
