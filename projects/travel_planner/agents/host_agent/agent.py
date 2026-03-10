from dotenv import load_dotenv
import textwrap

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .prompts import HOST_AGENT_INSTRUCTIONS

load_dotenv(override=True)

host_agent = Agent(
    name="host_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Coordinates travel planning by calling flight, stay, and activity agents.",
    instruction=textwrap.dedent(HOST_AGENT_INSTRUCTIONS).strip(),
)


USER_ID = "user_host"
SESSION_ID = "session_host"
APP_NAME = "host_app"

session_service = InMemorySessionService()

runner = Runner(
    agent=host_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


async def execute(request):
    # Ensure session exists
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    prompt = (
        f"Plan a trip to {request['destination']} from {request['start_date']} to {request['end_date']} "
        f"within a total budget of {request['budget']}."
        f"Call the flights, stays, and activities agents for results."
    )

    print("----- In host_agent -> execute() function ------")
    print(f"Prompt: {prompt}")
    print("------------------------------------------------")

    prompt = textwrap.dedent(prompt).strip()
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            return {"summary": event.content.parts[0].text}
