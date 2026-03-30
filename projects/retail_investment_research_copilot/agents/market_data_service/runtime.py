import asyncio
import os
import uuid
from typing import Any, Dict, Optional

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from logger import get_logger

logger = get_logger("retail_investment_copilot:market_data_service:runtime")


def flatten_text_from_event(event: Any) -> str:
    """Best-effort text extraction from an ADK event."""
    logger.info("In market_data_service::flatten_text_from_event()")
    content = getattr(event, "content", None)
    if not content:
        return ""
    parts = getattr(content, "parts", None) or []
    chunks: list[str] = []
    for part in parts:
        text = getattr(part, "text", None)
        if text:
            chunks.append(text)
    ret_val = "\n".join(chunks).strip()
    logger.debug(f"Exiting market_data_service::flatten_text_from_event() -> {ret_val}")
    return ret_val


async def run_agent_async(
    agent: Any,
    prompt: str,
    initial_state: Optional[Dict[str, Any]] = None,
) -> str:
    """Run an ADK agent in-process and return the final text response."""
    logger.info("In market_data_service::run_agent_async() ->")

    app_name = os.getenv("APP_NAME", "local_adk_app")
    user_id = os.getenv("ADK_USER_ID", "demo_user")
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service,
    )

    session = await runner.session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state=initial_state or {},
        session_id=str(uuid.uuid4()),
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_text = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=user_message,
        ):
            text = flatten_text_from_event(event)
            if text:
                final_text = text
    finally:
        await runner.close()

    logger.info(f"Exiting market_data_service::run_agent_async() -> {final_text}")
    return final_text


def run_agent(
    agent: Any,
    prompt: str,
    initial_state: Optional[Dict[str, Any]] = None,
) -> str:
    return asyncio.run(
        run_agent_async(agent=agent, prompt=prompt, initial_state=initial_state)
    )
