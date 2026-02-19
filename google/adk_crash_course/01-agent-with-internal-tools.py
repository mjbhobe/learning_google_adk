"""
01-agent-with-internal-tools.py

In this example, we extend the basic agent from previous example (00-basic-agent-no-tools.py)
by adding an INTERNAL Google Search tool. This allows the agent to fetch up-to-date
information from the web to answer user queries that require current data.

This is an example of a simple stand-alone agent that can generate full-day trip
itineraries based on mood, interests, and budget. It utilizes INTERNAL Google Search
tool to gather information about local attractions, restaurants, and activities to
create a personalized itinerary.

NOTE: code shared for learning purposes only! Use at your own risk.
"""

import os
import re
import asyncio
import argparse
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part
from utils import load_agent_config, run_agent_query

# load API keys
load_dotenv(override=True)

# load agent config from YAML file -- helps us externalize Agent params
# such as model, description, and instructions.
agent_config = load_agent_config("day_trip_agent")

# Step 1 -> Create an agent
day_trip_agent = Agent(
    name="day_trip_agent",
    model=agent_config["model"],
    description=agent_config["description"],
    instruction=agent_config["instruction"],
    tools=[google_search],
)


async def main():
    # Setup Argument Parser - add optional -q / --query argument to allow
    # users to input their own trip query. So for example, you could enter
    # the following on # the command line
    # uv run | python 01-day-trip-genie.py -q "Plan a fun day trip in Tokyo for a
    # family with young kids. Include outdoor activities and keep it budget-friendly."

    parser = argparse.ArgumentParser(description="Run the Day Trip Genie Agent")
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        help="The query for the agent (e.g., 'Plan a trip to Delhi')",
        # this is the default query, if user doesn't provide one using the -q | --query flag
        default="""Plan a relaxing and local food tasting trip near Mumbai, India. 
            Keep it affordable!""",
    )

    console = Console()
    args = parser.parse_args()
    session_service = InMemorySessionService()
    my_user_id = "adk_adventurer_001"
    query = args.query

    final_response = await run_agent_query(
        day_trip_agent,
        query,
        session_service,
        user_id=my_user_id,
    )
    console.print("[green]\n" + "-" * 50 + "[/green]")
    console.print("[green]✅ Final Response:[/green]")
    console.print(Markdown(final_response))
    console.print("[green]\n" + "-" * 50 + "[/green]")


if __name__ == "__main__":
    asyncio.run(main())
