import os
from dotenv import load_dotenv
import logging
import uuid
import textwrap
from rich.console import Console

from google.adk.agents import SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from .subagents.analyst_agent.agent import analyst_agent
from .subagents.reporter_agent.agent import reporter_agent

from logger import get_logger

# 1. Silence Pydantic's internal validation warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)

# 2. Silence LiteLLM's verbose logs (often the biggest culprit)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# 3. Silence ADK's model integration logs
# Note: Use 'google_adk' for the broad package or be specific as below
logging.getLogger("google_adk.models.lite_llm").setLevel(logging.WARNING)

logger = get_logger("buffet_bot.agents.workflow_agent")

root_agent = SequentialAgent(
    name="buffett_stock_analysis_workflow",
    # NOTE: we do NOT require a model for this type agent!
    # but we DO need to define sub-agents, which will run "left-to-right"
    sub_agents=[analyst_agent, reporter_agent],
    description="A pipeline that analyses raw financial metrics of stock and generates recommendation & a structured report",
)


async def execute(request):
    logger.info(f"In SequentialAgent -> execute() function")

    load_dotenv(override=True)
    assert os.getenv(
        "ANTHROPIC_API_KEY"
    ), "FATAL ERROR: ANTHROPIC_API_KEY not found in .env file!"

    APP_NAME = "buffet_bot"
    USER_ID = "buffet_bot_007"
    # generate a  new session id on every call!
    SESSION_ID = str(uuid.uuid4())

    console = Console()
    logger.info(f"   Incoming request: \n {request}")

    session_service = InMemorySessionService()

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # Ensure session exists
    await session_service.create_session(
        app_name=APP_NAME, 
        user_id=USER_ID, 
        session_id=SESSION_ID, 
        # pass in the request info in session to sub-agents
        state=request,
    )
    prompt = f"Analyse the stock {request['symbol']}"

    logger.info(f"    Executing prompt:\n {prompt}")

    prompt = textwrap.dedent(prompt).strip()
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
                logger.info(f"\n   final_response -> {final_response}\n")
                return {"analysis_report": final_response}