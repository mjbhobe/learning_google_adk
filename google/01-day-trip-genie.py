"""
01-day-trip-genie.py

This is an example of a simple stand-alone agent that can generate full-day trip itineraries based on mood, interests, and budget.

Components:
* Agent: The brain of the operation, defined by its instructions, tools, and the AI model it uses.
* Session: The conversation history. For this simple agent, it's just a container for a single request-response.
* Runner: The engine that connects the Agent and the Session to process your request and get a response.
"""

import os
import re
import asyncio
from dotenv import load_dotenv

import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part
from utils import load_agent_config, run_agent_query

# load API keys
load_dotenv(override=True)
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

agent_config = load_agent_config("day_trip_agent")

# Step 1 -> Create an agent
day_trip_agent = Agent(
    name="day_trip_agent",
    model=agent_config["model"],
    description=agent_config["description"],
    instruction=agent_config["instruction"],
    tools=[google_search],
)


# Step 2: Create a function to run the agent
async def run_day_trip_genie(
    agent: Agent,
    session_service: InMemorySessionService,
    user_id: str,
    query: str,
):
    # Create a new, single-use session for this query
    my_session = await session_service.create_session(
        app_name=agent.name, user_id=user_id
    )
    print(f"🗣️ User Query: '{query}'")

    await run_agent_query(agent, query, my_session, user_id)


# --- Initialize our Session Service ---
# This one service will manage all the different sessions in our notebook.
session_service = InMemorySessionService()
my_user_id = "adk_adventurer_001"
query = "Plan a relaxing and artsy day trip near Mumbai, India. Keep it affordable!"


async def main():
    await run_day_trip_genie(day_trip_agent, session_service, my_user_id, query)


if __name__ == "__main__":
    asyncio.run(main())
