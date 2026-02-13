"""
04-agent-with-memory.py

A truly intelligent agent needs to do more than just respond to one-off queries. It needs to remember the conversation, understand context, and adapt to feedback. This is achieved through proper session management. Think of a "loop agent" as an agent engaged in a continuous conversational loop, powered by its memory.

When you use the same session object for multiple, sequential queries, the agent can "see" the entire history of the conversation. This allows it to handle follow-up questions, correct itself based on feedback, and plan multi-step tasks.

NOTE: code shared for learning purposes only! Use at your own risk.
"""

import os
import asyncio
from typing import List
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from utils import load_agent_config, run_agent_query


# load API keys
load_dotenv(override=True)

console = Console()

multi_day_trip_planning_agent_config = load_agent_config(
    "multi-day-trip-planning-agent"
)

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

openai_model = LiteLlm(model="openai/gpt-4o")

multi_day_trip_planning_agent = Agent(
    name="db_agent",
    # model=openai_model,
    model=multi_day_trip_planning_agent_config["model"],
    description=multi_day_trip_planning_agent_config["description"],
    instruction=multi_day_trip_planning_agent_config["instruction"],
)


async def main():
    session_service = InMemorySessionService()
    my_user_id = "adk_adventurer_001"
    # NOTE: we'll need a common session across all queries
    my_session: Session = await session_service.create_session(
        app_name=multi_day_trip_planning_agent.name, user_id=my_user_id
    )

    # sample queries from a user that build on previous one
    queries: List[str] = [
        """Hi! I want to plan a 2-day trip to Lisbon, Portugal. I'm interested in historic sites and great local food.""",
        """That sounds pretty good, but I'm not a huge fan of castles. Can you replace the morning activity for Day 1 with something else historical?""",
        """Yes, the new plan for Day 1 is perfect! Please plan Day 2 now, keeping the food theme in mind.""",
    ]

    query = ""
    while True:
        query = Prompt.ask(
            "[bright_yellow] 🗣️Query (or type 'exit' or press Enter to quit): [/bright_yellow]",
            default="exit",
        )
        # query = input()
        if query.strip().lower() == "exit":
            console.print("[bright_yellow]Goodbye![/bright_yellow]")
            break

        # console.print(f"[green]🗣️ User Query:[/green] '{query}'")

        final_response = await run_agent_query(
            multi_day_trip_planning_agent,
            query,
            session_service,
            session=my_session,
            user_id=my_user_id,
        )

        console.print("[green]\n" + "-" * 50 + "\n[/green]")
        console.print("[green] 🧠 Response  :[/green]")
        console.print(Markdown(final_response))
        console.print("[green]\n" + "-" * 50 + "\n[/green]")


if __name__ == "__main__":
    asyncio.run(main())
