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
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from utils import load_agent_config, run_agent_query

""" 
used the following prompt to Google Gemini to generate hotel database

For each of the cities in the list below, find the names of top 5 hotels in the city. Then generate a JSON output in the format shown below where "city" is the city name from the list below (in all lower case), "hotel" is the name of the hotel you find, "rating" is a floating value between 1-5 (it can have decimal ratings with fraction values equal to 0.25 or 0.50 or 0.75 - for example 3.25 and 3.5 and 3.75 are valid ratings, but 3.4 is not!) and "reviews" is a number (between 0 and 7500)- generate fictitious values for rating & reviews. Return values in JSON format as below:

HOTEL_RATINGS = {
    {"city": "san francisco", "hotel": "The Grand Hotel", "rating": 4.5, "reviews":750},
    {"city": "san francisco", "hotel": "Seaside Inn", "rating": 4.5, "reviews":750},
    .....
}

Sunnyvale, CA
San Francisco, CA
Lake Tahoe, CA
San Jose, CA
Los Angeles, CA
Seattle, WA
Redmond, WA
Portland, OR
Las Vegas, NV
Phoenix, AZ
Denver, CO
Chicago, IL
Houston, TX
Dallas, TX
Tampa, FL
Miami, FL
New York, NY
Boston, MA
Washington, DC
St Louis, MO
Atlanta, GA
London, UK
Liverpool, UK
Manchester, UK
Paris, France
Madrid, Spain
Berlin, Germany
Bonn, Germany
Frankfurt, Germany
Rome, Italy
Milan, Italy
Cairo, Egypt
Cape Town, South Africa
Johannesburg, South Africa
Durban, South Africa
Dubai, UAE
Abu Dhabi, UAE
Sharjah, UAE
Mumbai, India
Pune, India
Nashik, India
New Delhi, India
Amritsar, India
Jaipur, India
Udaipur, India
Jodhpur, India
Indore, India
Bangalore, India
Bengaluru, India
Chennai, India
Hyderabad, India
Kochi, India
Panjim, India
Margao, India
Vasco da Gama, India
Singapore, Singapore
Tokyo, Japan
Seoul, South Korea
Sydney, Australia
Perth, Australia
Melbourne, Australia
Adelaide, Australia
Christchurch, New Zealand
Wellington, New Zealand
Auckland, New Zealand
"""

# load API keys
load_dotenv(override=True)
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

console = Console()

db_agent_config = load_agent_config("db_agent")
food_critic_agent_config = load_agent_config("food_critic_agent")
concierge_agent_config = load_agent_config("concierge_agent")
orchestration_agent_config = load_agent_config("orchestration_agent")

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

openai_model = LiteLlm(model="openai/gpt-4o")

# db_agent - an agent that fetches mock hotels data (generated
# using above prompt to Gemini & hard-coded in prompt!)
db_agent = LlmAgent(
    name="db_agent",
    model=openai_model,
    description=db_agent_config["description"],
    instruction=db_agent_config["instruction"],
)

# food_critic_agent - an agent that provides witty restaurant recommendations
food_critic_agent = LlmAgent(
    name="food_critic_agent",
    model=openai_model,
    description=food_critic_agent_config["description"],
    instruction=food_critic_agent_config["instruction"],
)

# concierge_agent - an agent that provided recommendations
# uses food_critic for food recommendations
concierge_agent = LlmAgent(
    name="concierge_agent",
    model=openai_model,
    description=concierge_agent_config["description"],
    instruction=concierge_agent_config["instruction"],
    # uses the food_critic_agent as a tool
    tools=[AgentTool(agent=food_critic_agent)],
)


# ----------------------------------------------------------
# tools for the orchestration agent
# ----------------------------------------------------------
async def call_db_agent(
    query: str,
    tool_context: ToolContext,
) -> str:
    print("--- TOOL CALL: call_db_agent ---")
    agent_tool = AgentTool(agent=db_agent)
    db_agent_output = await agent_tool.run_async(
        args={"request": query}, tool_context=tool_context
    )
    # Store the retrieved data in the context's state
    tool_context.state["retrieved_data"] = db_agent_output
    return db_agent_output


async def call_concierge_agent(
    question: str,
    tool_context: ToolContext,
):
    """
    After getting data with call_db_agent, use this tool to get travel advice, opinions, or recommendations.
    """
    print("--- TOOL CALL: call_concierge_agent ---")
    # Retrieve the data fetched by the previous tool
    input_data = tool_context.state.get("retrieved_data", "No data found.")

    # Formulate a new prompt for the concierge, giving it the data context
    question_with_data = f"""
    Context: The database returned the following data: {input_data}

    User's Request: {question}
    """

    agent_tool = AgentTool(agent=concierge_agent)
    concierge_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    return concierge_output


# this is the main orchestration agent, which uses tools that call above agents
# to do the work. User will interact with this agent
orchestration_agent = Agent(
    name="trip_data_concierge",
    model=openai_model,
    description=orchestration_agent_config["description"],
    instruction=orchestration_agent_config["instruction"],
    tools=[call_db_agent, call_concierge_agent],
)


async def main():
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
            orchestration_agent,
            query,
            session_service,
            my_user_id,
        )

        console.print("[green]\n" + "-" * 50 + "\n[/green]")
        console.print("[green] :[/green]")
        console.print(Markdown(final_response))
        console.print("[green]\n" + "-" * 50 + "\n[/green]")


if __name__ == "__main__":
    asyncio.run(main())
