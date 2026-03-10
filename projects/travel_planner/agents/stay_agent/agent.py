from dotenv import load_dotenv
import textwrap

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .prompts import STAY_AGENT_INSTRUCTIONS

stay_agent = Agent(
    name="stay_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Suggests hotel or stay options for a destination.",
    instruction=textwrap.dedent(STAY_AGENT_INSTRUCTIONS).strip(),
)

USER_ID = "user_stay"
SESSION_ID = "session_stay"
APP_NAME = "stay_app"

session_service = InMemorySessionService()
runner = Runner(
    agent=stay_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


async def execute(request):
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    prompt = textwrap.dedent(
        f"User is staying in {request['destination']} from {request['start_date']} to {request['end_date']} "
        f"with a budget of {request['budget']}. Suggest stay options."
    ).strip()

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            return {"stays": event.content.parts[0].text}
