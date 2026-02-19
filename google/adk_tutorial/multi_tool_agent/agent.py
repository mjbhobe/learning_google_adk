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


# first let's test this
async def main():
    city: str = "London"
    data = await get_weather(city)
    time_str = await get_time(city)

    print(f"Weather in {data['city']}, {data['country']}:")
    print(f"- Temp: {data['temperature_c']}°C")
    print(f"- Wind: {data['wind_speed']} km/h")
    print(f"Current time in {city}: {time_str}")


if __name__ == "__main__":
    asyncio.run(main())
