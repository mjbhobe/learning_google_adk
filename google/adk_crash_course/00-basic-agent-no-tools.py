"""
00-basic-agent-no-tools.py

This is an example of a basic agent, which relies on it's pretrained knowledge to
respond to user's queries. It will NOT be able to fetch the latest info from the web
as it does not have any tools support yet! Also no session memory, so each query is
distinct and LLM has no link to previous questions or responses.

NOTE: code shared for learning purposes only! Use at your own risk.
"""

import os
import asyncio
import argparse
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService

from utils import load_agent_config, run_agent_query

load_dotenv(override=True)

agent_config = load_agent_config("basic_agent")

# this is an agent that uses a Google Gemini model
greeting_agent = Agent(
    name="greeting_agent",
    model=agent_config["model"],  # gemini-2.5-flash
    description=agent_config["description"],
    instruction=agent_config["instruction"],
)


# NOTE: ensure you have an entry for OPENAI_API_KEY in your .env file!
# also add google-adk[extensions] to your local Python environment
openai_model = LiteLlm(model="openai/gpt-4o")

openai_greeting_agent = LlmAgent(
    name="openai_greeting_agent",
    # if you plan to use a Google LLM (for example gemini-2.5-flash), then
    # use it as below (no need to instantiate a LiteLlm instance)
    # model = "gemini-2.5-flash",  # <<<< for Google LLMs
    model=openai_model,
    description=agent_config["description"],
    instruction=agent_config["instruction"],
)


async def main():
    console = Console()
    session_service = InMemorySessionService()
    my_user_id = "adk_adventurer_001"

    query = ""
    while True:
        # a simple console based chat with Agent
        query = Prompt.ask(
            "[bright_yellow]Your question (or type 'exit' or press Enter to quit): [/bright_yellow]",
            default="exit",
        )
        # query = input()
        if query.strip().lower() == "exit":
            console.print("[bright_yellow]Goodbye![/bright_yellow]")
            break

        console.print(f"[green]🗣️ User Query:[/green] '{query}'")

        final_response = await run_agent_query(
            # greeting_agent,
            openai_greeting_agent,
            query,
            session_service=session_service,
            user_id=my_user_id,
        )
        console.print("[green]\n" + "-" * 50 + "[/green]")
        console.print("[green]✅ Agent Response:[/green]")
        console.print(Markdown(final_response))
        console.print("[green]\n" + "-" * 50 + "[/green]")


if __name__ == "__main__":
    asyncio.run(main())
