"""
03-agent-as-a-tool.py

This example illustrates how to build complex systems where a primary agent, often called an Orchestrator or Router, delegates tasks to other, more focused agents.

In this example, we have a top-level agent, the `trip_data_concierge_agent`, acts as the Orchestrator. It has two tools at its disposal:
 * `call_db_agent`: A function that internally calls our db_agent to fetch raw data.
 * `call_concierge_agent`: A function that calls the concierge_agent.
 * The concierge_agent itself has a tool: the food_critic_agent.

The flow for a complex query is:
 1. User asks the `trip_data_concierge_agent` for a hotel and a nearby restaurant.
 2. The Orchestrator first calls `call_db_agent` to get hotel data.
 3. The data is saved in `tool_context.state`.
 4. The Orchestrator then calls `call_concierge_agent`, which retrieves the hotel data from the context.
 5. The concierge_agent receives the request and decides it needs to use its own tool, the food_critic_agent.
 6. The `food_critic_agent` provides a witty recommendation.
 7. The `concierge_agent` gets the critic's response and politely formats it.
 8. This final, polished response is returned to the Orchestrator, which presents it to the user.

NOTE: code shared for learning purposes only! Use at your own risk.
"""

import os
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from utils import load_agent_config, run_agent_query

# load API keys
load_dotenv(override=True)
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

db_agent_config = load_agent_config("db_agent")
food_critic_agent_config = load_agent_config("food_critic_agent")


# db_agent - an agent that fetches mock hotels data
db_agent = Agent(
    name="db_agent",
    model=db_agent_config["model"],
    description=db_agent_config["description"],
    instruction=db_agent_config["instruction"],
)

# food_critic_agent - an agent that provides witty restaurant recommendations
food_critic_agent = Agent(
    name="food_critic_agent",
    model=food_critic_agent["model"],
    description=food_critic_agent["description"],
    instruction=food_critic_agent["instruction"],
)


async def main():
    console = Console()
    session_service = InMemorySessionService()
    my_user_id = "adk_adventurer_001"

    query = ""
    while True:
        query = Prompt.ask(
            "[bright_yellow]Query (or type 'exit' or press Enter to quit): [/bright_yellow]",
            default="exit",
        )
        # query = input()
        if query.strip().lower() == "exit":
            console.print("[bright_yellow]Goodbye![/bright_yellow]")
            break

        # console.print(f"[green]🗣️ User Query:[/green] '{query}'")

        final_response = await run_agent_query(
            weather_agent,
            query,
            session_service,
            my_user_id,
        )

        console.print("[green]\n" + "-" * 50 + "\n[/green]")
        console.print("[green]🌤️ Live Weather:[/green]")
        console.print(Markdown(final_response))
        console.print("[green]\n" + "-" * 50 + "\n[/green]")


if __name__ == "__main__":
    asyncio.run(main())
