"""
00-basic-agent.py

This is an example of a basic agent, which relies on it's pretrained knowledge to respond to user's
queries. It will first ask for the user's name, greet them and then ansewer their questions.

NOTE: code shared for learning purposes only! Use at your own risk.
"""

import os
import asyncio
import argparse
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService

from utils import load_agent_config, run_agent_query

load_dotenv(override=True)
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

agent_config = load_agent_config("basic_agent")

greeting_agent = Agent(
    name="greeting_agent",
    model=agent_config["model"],
    description=agent_config["description"],
    instruction=agent_config["instruction"],
)


async def main():
    console = Console()
    session_service = InMemorySessionService()
    my_user_id = "adk_adventurer_001"

    query = ""
    while True:
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
            greeting_agent,
            query,
            session_service,
            my_user_id,
        )
        console.print("[green]\n" + "-" * 50 + "\n[/green]")
        console.print("[green]✅Response:[/green]")
        console.print(Markdown(final_response))
        console.print("[green]\n" + "-" * 50 + "\n[/green]")


if __name__ == "__main__":
    asyncio.run(main())
