from dotenv import load_dotenv
import textwrap

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .prompts import FLIGHT_AGENT_INSTRUCTIONS

USER_ID = "user_1"
SESSION_ID = "session_001"
APP_NAME = "flight_app"


flight_agent = Agent(
    name="flight_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Suggests flight options for a destination.",
    instruction=textwrap.dedent(FLIGHT_AGENT_INSTRUCTIONS).strip(),
)


session_service = InMemorySessionService()
runner = Runner(
    agent=flight_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


async def execute(request):
    # 🔧 Ensure session is created before running the agent
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    prompt = textwrap.dedent(
        f"User is flying from {request['origin']} to {request['destination']} "
        f"from {request['start_date']} to {request['end_date']}, with a budget "
        f"of {request['budget']}. "
        "Suggest 2-3 realistic flight options. For each option, include airline, "
        "departure time, return time, price, and mention if it's direct or has layovers."
    ).strip()

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            return {"flights": event.content.parts[0].text}
