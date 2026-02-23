"""
10-agent-with-structured-output.py

Examples shows how we can get structured output from
our Agent.

"""

import asyncio
from dotenv import load_dotenv
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService

from utils import load_agent_config, run_agent_query, web_search

# load our API keys from .env file
load_dotenv(override=True)


class ConsultantTypeEnum(Enum):
    PSYCHOLOGIST = "psychologist"
    PSYCHIATRIST = "psychiatrist"
    THERAPIST = "therapist"
    NUTRITIONIST = "nutritionist"
    PERSONAL_TRAINER = "personal_trainer"
    LIFE_COACH = "life_coach"
    FINANCIAL_ADVISOR = "financial_advisor"
    BUSINESS_COACH = "business_coach"
    CAREER_COACH = "career_coach"
    GENERAL_HELPER = "general_helper"


# --- structured output format of our ProblemAnalysis agent --------


class ProblemAnalysis(BaseModel):
    consultant_type: ConsultantTypeEnum
    identified_issues_summary: str = Field(
        description="A brief summary of the core issues identified from the user's query."
    )


problem_analysis_agent_config = load_agent_config("problem_analysis_agent")
problem_analysis_agent = LlmAgent(
    name="Problem Analyzer Agent",
    model=problem_analysis_agent_config["model"],
    description=problem_analysis_agent_config["description"],
    instruction=problem_analysis_agent_config["instruction"],
    output_format=ProblemAnalysis,
)


async def main():
    session_service = InMemorySessionService()
    app_name = "agent_with_structured_output_app"
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
            problem_analysis_agent,
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
