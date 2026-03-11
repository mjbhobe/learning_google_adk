import os
from dotenv import load_dotenv
import textwrap

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .prompts import FLIGHT_AGENT_INSTRUCTIONS

load_dotenv(override=True)
assert os.getenv("OPENAI_API_KEY"), "FATAL: flight_agent -> OPENAI_API_KEY not set!"

USER_ID = "user_flights"
SESSION_ID = "session_flights"
APP_NAME = "flight_app"


flight_agent = Agent(
    name="flight_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Suggests flight options for a destination.",
    instruction=textwrap.dedent(FLIGHT_AGENT_INSTRUCTIONS).strip(),
)


async def execute(request):

    session_service = InMemorySessionService()
    runner = Runner(
        agent=flight_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # 🔧 Ensure session is created before running the agent
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    prompt = (
        f"User is flying from {request['origin']} to {request['destination']} "
        f"from {request['start_date']} to {request['end_date']}, with a budget "
        f"of {request['budget']}. "
        "Suggest 2-3 realistic flight options. For each option, include airline, "
        "departure time, return time, price, and mention if it's direct or has layovers."
    )

    print("----- In flight_agent -> execute() function ------")
    print(f"Prompt: {prompt}")
    print("------------------------------------------------")

    prompt = textwrap.dedent(prompt).strip()
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            return {"flights": event.content.parts[0].text}
