"""
05-router-agent.py

So far we have handled simple tasks that rely on 1 agent. Most tasks are too complex
for 1 agent to handle - for example if the user asks "Find me a great Italian restaurant
in Mumbai and tell me how to get there" - this task requires 2 different skills:
  a. Restaurant recommendation and
  b. Nagivation.

In this example we'll use a top Router agent, which will "direct" flow to << TODO >>


NOTE: code shared for learning purposes only! Use at your own risk.
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

day_trip_agent_config = load_agent_config("day_trip_agent")
foodie_agent_config = load_agent_config("foodie_agent")
foodie_formatter_agent_config = load_agent_config("foodie_formatter_agent")
weekend_guide_agent_config = load_agent_config("weekend_guide_agent")
transportation_agent_config = load_agent_config("transportation_agent")
router_agent_config = load_agent_config("router_agent")


# NOTE: ensure you have an entry for OPENAI_API_KEY in your .env file!
# also add google-adk[extensions] to your local Python environment
openai_model = LiteLlm(model="openai/gpt-4o")

# using the same agent we developed in 01-agent-basics.py as a tool in our router agent
day_trip_agent = LlmAgent(
    name="day_trip_agent",
    # model=day_trip_agent_config["model"],
    model=openai_model,
    description=day_trip_agent_config["description"],
    instruction=day_trip_agent_config["instruction"],
    tools=[web_search],
)


# we will force structured data from the food_agent, which
# returns restaurant recommendations (i.e. name & reason for choosing this restaurant)
class FoodieResponse(BaseModel):
    restaurant_name: str = Field(description="The name of the recommended restaurant")
    reason: str = Field(description="Brief reason why this was chosen")


foodie_agent = LlmAgent(
    name="foodie_agent",
    # model=foodie_agent_config["model"],
    model=openai_model,
    description=foodie_agent_config["description"],
    instruction=foodie_agent_config["instruction"],
    tools=[web_search],
    # output_schema=FoodieResponse,
    output_key="raw_foodie_output",  # This is the "magic" key for the session state
)

foodie_formatter_agent = LlmAgent(
    name="foodie_formatter_agent",
    # model=foodie_agent_config["model"],
    model=openai_model,
    description=foodie_formatter_agent_config["description"],
    instruction=foodie_formatter_agent_config["instruction"],
    output_schema=FoodieResponse,
    output_key="structured_foodie_data",  # This is the "magic" key for the session state
)

foodie_flow_agent = SequentialAgent(
    name="foodie_sequential_pipeline",
    sub_agents=[foodie_agent, foodie_formatter_agent],
)

weekend_guide_agent = LlmAgent(
    name="weekend_guide_agent",
    # model=weekend_guide_agent_config["model"],
    model=openai_model,
    description=weekend_guide_agent_config["description"],
    instruction=weekend_guide_agent_config["instruction"],
    tools=[web_search],
)

transportation_agent = LlmAgent(
    name="transportation_agent",
    # model=transportation_agent_config["model"],
    model=openai_model,
    description=transportation_agent_config["description"],
    instruction=transportation_agent_config["instruction"],
    tools=[web_search],
)

# -----------------------------------------
# the router - the brain of our operations
# -----------------------------------------
router_agent = LlmAgent(
    name="router_agent",
    # model=router_agent_config["model"],
    model=openai_model,
    description=router_agent_config["description"],
    instruction=router_agent_config["instruction"],
)

# a dict to point to our worker agents
worker_agents = {
    "day_trip_agent": day_trip_agent,
    "foodie_agent": foodie_agent,
    "weekend_guide_agent": weekend_guide_agent,
    "transportation_agent": transportation_agent,
}

"""
Process Flow:
                    +---------------------+
                    |    User Query 🗣️     |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    |   Router Agent 🤖    |
                    |  (Classify Request) |
                    +----------+----------+
                               |
          +--------------------+----------------------+
          |                    |                      |
          v                    v                      v
  +-----------------+   +--------------------+  +------------------+
  |  foodie_agent   |   | weekend_guide_agent|  |  day_trip_agent  |
  |  🍣 Food Search |   | 🎉 Event Discovery |  | 🧳 Trip Planner  |
  +-----------------+   +--------------------+  +------------------+
          |
          v
  +----------------------------+            (if combo request)
  |  Restaurant Recommendation |---------------------------+
  |  ex: "Best sushi is at X"  |                           |
  +----------------------------+                           v
                                                    +-----------------------+
                                                    | transportation_agent  |
                                                    | 🚗 Get Directions     |
                                                    +-----------------------+
                                                    | Input: origin, place  |
                                                    | Output: directions    |
                                                    +-----------------------+
Final Output: 🍽️ Recommendation + 🚗 Route Info
"""


async def run_sequential_app():
    queries = [
        # "I want to eat the best Italian in Palo Alto.",  # Should go to foodie_agent
        # "Are there any cool outdoor concerts this weekend?",  # Should go to weekend_guide_agent
        "Find me the best Indian restaurant in Palo Alto and then tell me how to get there from the Caltrain station.",  # Should trigger the COMBO
    ]

    session_service = InMemorySessionService()
    my_user_id = "adk_adventurer_001"

    for query in queries:
        console.print(
            f"[green]\n{'='*60}\n🗣️ Processing New Query: '{query}'\n{'='*60}[/green]"
        )

        # 1. Ask the Router Agent to choose the right agent or workflow
        router_session = await session_service.create_session(
            app_name=router_agent.name, user_id=my_user_id
        )
        console.print("[green]🧠 Asking the router agent to make a decision...[/green]")
        chosen_route = await run_agent_query(
            router_agent,
            query,
            session_service,
            session=router_session,
            user_id=my_user_id,
            is_router=True,
        )
        chosen_route = chosen_route.strip().replace("'", "")
        console.print(
            f"[yellow]🚦 Router has selected route: '{chosen_route}'[/yellow]"
        )

        # 2. Execute the chosen route
        if chosen_route == "find_and_navigate_combo":
            console.print(
                "[green]\n--- Starting Find and Navigate Combo Workflow ---[/green]"
            )

            # STEP 2a: Run the foodie_agent first
            foodie_flow_session = await session_service.create_session(
                app_name=foodie_flow_agent.name, user_id=my_user_id
            )
            foodie_response = await run_agent_query(
                foodie_flow_agent,
                query,
                session_service,
                session=foodie_flow_session,
                user_id=my_user_id,
            )

            pydantic_result = foodie_flow_session.state.get("structured_foodie_data")
            if pydantic_result:
                # get the recommendations from session state
                # state = await foodie_session.get_state()
                # foodie_data = state.get("foodie_data")
                # destination = (
                #     foodie_response.restaurant_name
                #     if isinstance(foodie_response, FoodieResponse)
                #     else "Unknown"
                # )
                destination = pydantic_result.restaurant_name
                console.print(
                    f"[green] ✅ {foodie_flow_agent.name} \n Response:\n {pydantic_result} \n Destination: {destination} [/green]"
                )

                # STEP 2b: Extract the destination from the first agent's response
                # (This is a simple regex, a more robust solution might use a structured output format)
                # match = re.search(r"\*\*(.*?)\*\*", foodie_response)
                # if not match:
                #     console.print(
                #         "[red]🚨 Could not determine the restaurant name from the response.[/red]"
                #     )
                #     continue
                # destination = match.group(1)
                # console.print(f"[blue]💡 Extracted Destination: {destination}[/blue]")

                # STEP 2c: Create a new query and run the transportation_agent
                directions_query = f"Give me directions to {destination} from the Palo Alto Caltrain station."
                console.print(
                    f"[green]\n🗣️ New Query for Transport Agent: '{directions_query}'[/green]"
                )
                transport_session = await session_service.create_session(
                    app_name=transportation_agent.name, user_id=my_user_id
                )
                response = await run_agent_query(
                    transportation_agent,
                    directions_query,
                    session_service,
                    session=transport_session,
                    user_id=my_user_id,
                )
                console.print(
                    f"[green] ✅ {transportation_agent.name} Response:\n {Markdown(response)}[/green]"
                )

                console.print("[green]--- Combo Workflow Complete ---[/green]")
            else:
                console.print(
                    "[red]🚨 Could not retrieve structured data from the foodie agent. Aborting combo workflow.[/red]"
                )
        elif chosen_route in worker_agents:
            # This is a simple, single-agent route
            worker_agent = worker_agents[chosen_route]
            worker_session = await session_service.create_session(
                app_name=worker_agent.name, user_id=my_user_id
            )
            response = await run_agent_query(
                worker_agent,
                query,
                session_service,
                session=worker_session,
                user_id=my_user_id,
            )
            console.print(
                f"[green] ✅ {worker_agent.name} response:\n {response}[/green]"
            )
        else:
            console.print(
                f"[red]🚨 Error: Router chose an unknown route: '{chosen_route}'[/red]"
            )


async def main():
    await run_sequential_app()


if __name__ == "__main__":
    asyncio.run(main())
