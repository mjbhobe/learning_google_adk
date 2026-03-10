from dotenv import load_dotenv
import textwrap
import json

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .prompts import ACTIVITY_AGENT_INSTRUCTIONS

load_dotenv(override=True)

activities_agent = Agent(
    name="activities_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Suggests interesting activities for the user at a destination.",
    instruction=textwrap.dedent(ACTIVITY_AGENT_INSTRUCTIONS).strip(),
)


USER_ID = "user_activities"
SESSION_ID = "session_activities"
APP_NAME = "activities_app"

# configure a runner for the above agent
session_service = InMemorySessionService()
runner = Runner(
    agent=activities_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


# and a function to execute the agent
async def execute(request):
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    prompt = textwrap.dedent(
        f"User is flying to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}."
        f"Suggest 2-3 activities, each with name, description, price estimate, and duration. "
        f"Respond in JSON format using the key 'activities' with a list of activity objects."
    ).strip()
    # build user-query
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    # and run the user-query
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "activities" in parsed and isinstance(parsed["activities"], list):
                    return {"activities": parsed["activities"]}
                else:
                    print("'activities' key missing or not a list in response JSON")
                    return {"activities": response_text}  # fallback to raw text
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"activities": response_text}  # fallback to raw text
