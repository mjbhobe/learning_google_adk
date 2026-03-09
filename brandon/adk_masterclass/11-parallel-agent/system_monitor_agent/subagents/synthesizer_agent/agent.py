"""
System Report Synthesizer Agent

This agent is responsible for synthesizing information from other agents
to create a comprehensive system health report.
"""

from dotenv import load_dotenv
import logging

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# 1. Silence Pydantic's internal validation warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)

# 2. Silence LiteLLM's verbose logs (often the biggest culprit)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# 3. Silence ADK's model integration logs
# Note: Use 'google_adk' for the broad package or be specific as below
logging.getLogger("google_adk.models.lite_llm").setLevel(logging.WARNING)

load_dotenv()

openai_model = LiteLlm(model="openai/gpt-4o")

system_report_synthesizer = Agent(
    name="system_report_synthesizer",
    model=openai_model,
    instruction="""You are a System Report Synthesizer.

        Your task is to create a comprehensive system health report by combining information from:
        - CPU information: {cpu_info}
        - Memory information: {memory_info}
        - Disk information: {disk_info}

        Create a well-formatted report with:
        1. An executive summary at the top with overall system health status
        2. Sections for each component with their respective information
        3. Recommendations based on any concerning metrics

        Use markdown formatting to make the report readable and professional.
        Highlight any concerning values and provide practical recommendations.
        """,
    description="Synthesizes all system information into a comprehensive report",
)
