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
from rich.console import Console
from rich.markdown import Markdown

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.sessions import InMemorySessionService

from utils import load_agent_config, run_agent_query, web_search

# load our API keys from .env file
load_dotenv(override=True)
console = Console()


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


class ConsultationResp(BaseModel):
    consultant_type: ConsultantTypeEnum
    identified_issues_summary: str
    suitability_explanation: str
    key_questions_to_consider: List[str]
    initial_actionable_steps: List[str]
    disclaimer: str


# ----------- the initial problem analysis agent -----------------
problem_analysis_agent_config = load_agent_config("problem_analysis_agent")
problem_analysis_agent = LlmAgent(
    name="ProblemAnalyzerAgent",
    model=problem_analysis_agent_config["model"],
    description=problem_analysis_agent_config["description"],
    instruction=problem_analysis_agent_config["instruction"],
    # this key 'formats' output to specific schema
    output_schema=ProblemAnalysis,
    output_key="problem_analysis_result",
)

# ----------- the consultation agent -----------------
consultation_agent_config = load_agent_config("consultation_agent")
consultation_agent = LlmAgent(
    name="ConsultationAgent",
    model=consultation_agent_config["model"],
    description=consultation_agent_config["description"],
    instruction=consultation_agent_config["instruction"],
    # this key 'formats' output to specific schema
    output_schema=ConsultationResp,
    output_key="final_consultation_response",
)

root_agent = SequentialAgent(
    name="StructuredConsultationAgent",
    sub_agents=[problem_analysis_agent, consultation_agent],
)


async def main():
    session_service = InMemorySessionService()
    app_name = "agent_with_structured_output_app"
    my_user_id = "adk_adventurer_001"

    # sample prompts to test the problem analysis agent
    prompts = {
        #        "PSYCHOLOGIST": "I've been having intrusive negative thoughts, frequent panic-like episodes, and trouble concentrating at work for months—I'm worried this is affecting my relationships; can you help me understand what's going on and what steps I should take?",
        #        "PSYCHOLOGIST": "Lately I feel numb and unmotivated, I cry unexpectedly, and my sleep is all over the place—I'm not sure if this is depression or burnout; what signs should I look for and how should I start addressing it?",
        #        "PSYCHIATRIST": "My anxiety is severe, and I've tried therapy with limited improvement; I also notice physical symptoms and racing thoughts—could medication help and what are the options I should discuss with a prescriber?",
        #        "PSYCHIATRIST": "I've had mood swings with periods of very high energy followed by deep lows that last days—I'm worried about bipolar disorder and want to know what diagnostic steps and medication strategies are appropriate.",
        #        "THERAPIST": "My partner and I keep having the same arguments about communication; we both feel unheard and keep revisiting old hurts—can you suggest therapeutic approaches or exercises we can try to improve our relationship?",
        #        "THERAPIST": "I grew up in a household where emotions were dismissed and now I struggle with setting boundaries at work and with family—what therapeutic techniques can help me build assertiveness and emotional regulation?",
        #        "NUTRITIONIST": "I've been feeling sluggish, my digestion is inconsistent, and I recently gained weight despite not changing much—can you suggest a nutrition plan, potential food sensitivities to test for, and simple lab markers to check?",
        #        "NUTRITIONIST": "I'm a vegetarian training for a half-marathon and worried I'm not getting enough iron and protein—what meal and supplement plan would optimize my performance and recovery?",
        #        "PERSONAL_TRAINER": "I have a busy schedule but want to lose 10 lbs and build strength—what realistic 8-week workout plan and weekly time commitment would you recommend given I can train 3x/week?",
        #        "PERSONAL_TRAINER": "I've been stuck at the same deadlift weight for months and get lower-back fatigue—can you analyze my possible technique or programming issues and suggest corrections and progressions?",
        #        "LIFE_COACH": "I hit a career plateau and feel unsure of my next goals; I want more purpose but get overwhelmed when I try to plan—can you help me clarify priorities and create an actionable 90-day plan?",
        #        "LIFE_COACH": "I keep procrastinating on starting my side business despite wanting freedom—what mindset shifts and daily habits can I implement to move from idea to first customer within 60 days?",
        "FINANCIAL_ADVISOR": "I have $30k in savings, $12k in student loans (5% interest), and a 401(k) matching 4%—should I prioritize paying down debt, investing more, or building an emergency fund, given my goal to buy a house in 2 years?",
        #        "FINANCIAL_ADVISOR": "I'm self-employed with irregular income—how should I structure a budget, tax-advantaged retirement contributions, and a cash buffer to smooth seasons and plan for retirement?",
        #        "BUSINESS_COACH": "I'm launching a subscription-based product but my churn rate is high after month one—can you help identify potential product-market fit issues and suggest experiments to improve retention?",
        #        "BUSINESS_COACH": "Our small team struggles with scaling processes as we grow from 5 to 20 people; what organizational changes and leadership practices should we prioritize to avoid chaos?",
        #        "CAREER_COACH": "I've been passed over for promotion twice despite strong performance—how should I analyze the gap, communicate with managers, and position myself for the next opportunity?",
        #        "CAREER_COACH": "I'm transitioning from academia to industry and need to reframe my CV and interview stories—can you help translate my research experience into clear, hireable skills and achievements?",
        #        "GENERAL_HELPER": "I'm juggling house renovations, work deadlines, and family care and feel overwhelmed—can you help me create a prioritized checklist and short daily routine to get back on track?",
        #        "GENERAL_HELPER": "I need help drafting a clear, polite email to request a deadline extension from a client while protecting the relationship—can you write a few concise options and explain when to use each?",
    }

    # lets iterate through the prompts
    for consultant, issue in prompts.items():

        console.print("[green]\n" + "-" * 50 + "[/green]")
        console.print(f"\n[bright_blue]Consultant Type:[/bright_blue] {consultant}")
        console.print(f"[bright_white]Issue:[/bright_white] {issue}")
        console.print("[yellow]\n" + "-" * 50 + "[/yellow]")

        final_response = await run_agent_query(
            # greeting_agent,
            root_agent,
            issue,
            session_service=session_service,
            user_id=my_user_id,
        )

        console.print("[yellow]\n" + "-" * 50 + "[/yellow]")

        console.print("[green]✅ Agent Response:[/green]")
        console.print(final_response)
        console.print("[green]\n" + "-" * 50 + "[/green]")


if __name__ == "__main__":
    asyncio.run(main())
