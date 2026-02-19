"""
06-sequential-agent.py

In the previous code (05-router-agent.py), we saw how to use custom Python code to
connect agents together. This technique can quickly get very complicated.
In this example, we'll refactor our workflow to use a powerful, built-in ADK feature
designed specifically for this: the **SequentialAgent**.

The **SequentialAgent** is a workflow agent. It's NOT powered by an LLM itself; instead,
its only job is to execute a list of other agents in a strict, predefined order.

The real magic ✨ is how it passes information. The ADK uses a shared state dictionary
that each agent in the sequence can read from and write to.

Our New Workflow:
 * Foodie Agent: Finds the restaurant and saves the name to state['destination'].
 * Transportation Agent: Automatically reads state['destination'] and uses it to find directions.
   This means we no longer need custom Python code to extract text or build new queries!
   The ADK handles the plumbing for us.

"""

import re
import asyncio
from typing import List
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService, Session
from google.adk.tools import google_search
from google.adk.tools import ToolContext

from utils import load_agent_config, run_agent_query, web_search


# load API keys
load_dotenv(override=True)
console = Console()

# load our agents config
foodie_agent_config = load_agent_config("foodie_agent_2")
transportation_agent_config = load_agent_config("transportation_agent_2")
sequential_agent_config = load_agent_config("sequential_agent")
router_agent_config = load_agent_config("router_agent_2")

# define our agents
foodie_agent = LlmAgent(
    name="foodie_agent",
    model=LiteLlm(model="openai/gpt-4o"),
    description=foodie_agent_config["description"],
    instruction=foodie_agent_config["instruction"],
    tools=[web_search],
    # this is the session key the next agent in sequence will use
    # to extract output of this agent
    output_key="destination",
)

transportation_agent = LlmAgent(
    name="transportation_agent",
    model=LiteLlm(model="openai/gpt-4o"),
    description=transportation_agent_config["description"],
    instruction=transportation_agent_config["instruction"],
    tools=[web_search],
    # this agent reads the output of the previous agent in the sequence
    # input_key="destination",
)

# ----- Router Agent - executes foodie agent and transportation agent in sequence ------
find_and_navigate_agent = SequentialAgent(
    name="find_and_navigate_agent",
    sub_agents=[foodie_agent, transportation_agent],
    description="A workflow that first finds a location and then provides directions to it.",
)

# worker agents lookup
worker_agents = {
    # "day_trip_agent": day_trip_agent,
    "foodie_agent": foodie_agent,
    # "weekend_guide_agent": weekend_guide_agent,
    "find_and_navigate_agent": find_and_navigate_agent,  # Add the new sequential agent
}

router_agent = LlmAgent(
    name="router_agent",
    model=LiteLlm(model="openai/gpt-4o"),
    description=router_agent_config["description"],
    instruction=router_agent_config["instruction"],
)


async def main():
    session_service = InMemorySessionService()
    my_user_id = "adk_adventurer_001"
    # NOTE: we'll need a common session across all queries
    my_session: Session = await session_service.create_session(
        app_name=find_and_navigate_agent.name, user_id=my_user_id
    )

    # sample queries from a user that build on previous one
    queries: List[str] = [
        # should call foodie_agent
        "Find me the best Burmese restaurant in South Mumbai",
        # should call find_and_navigate_agent
        """Find me the best Burmese restaurant in South Mumbai and then tell me how to
        get there from Churchgate station""",
        # should skip everything
        "Who is Sachin Tendulkar?",
    ]

    for query in queries:
        console.print(f"[yellow]🗣️ User Query: '{query}'[/yellow]")
        console.print(f"[blue]🗣️ Asking router ...[/blue]")

        # first ask the router agent to pick the agent to route to
        chosen_route = await run_agent_query(
            router_agent,
            query,
            session_service,
            # session=my_session,
            user_id=my_user_id,
            is_router=True,
        )
        chosen_route = chosen_route.strip().replace("'", "")
        console.print(f"[green] Router has selected route: '{chosen_route}'[/green]")

        if chosen_route in worker_agents:
            console.print(f"[blue] Handing off to '{chosen_route}'...[/blue]")
            final_response = await run_agent_query(
                worker_agents[chosen_route],
                query,
                session_service,
                # session=my_session,
                user_id=my_user_id,
            )
            console.print("[green]\n" + "-" * 50 + "[/green]")
            console.print("[green] 🧠 Final Response  :[/green]")
            console.print(Markdown(final_response))
            console.print("[green]\n" + "-" * 50 + "[/green]")
        else:
            console.print(
                f"[red]⚠️ Selected route '{chosen_route}' not recognized! Skipping...[/red]"
            )


if __name__ == "__main__":
    asyncio.run(main())
