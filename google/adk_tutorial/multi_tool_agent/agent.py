"""
01_multi_tool_agent.py - develop a Google ADK powered agent with mutiple tools

"""

import asyncio
from dotenv import load_dotenv

from google.adk.agents import Agent

from tools import get_weather, get_time

# load API keys from .env file
load_dotenv(override=True)

root_agent = Agent(
    name="multi_tool_agent",
    model="gemini-2.5-flash",
    description=("Agent to answer questions about the time and weather in a city."),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_time],
)
