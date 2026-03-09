"""
CPU Information Agent

This agent is responsible for gathering and analyzing CPU information.
"""

from dotenv import load_dotenv
import logging

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .tools import get_cpu_info

# 1. Silence Pydantic's internal validation warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)

# 2. Silence LiteLLM's verbose logs (often the biggest culprit)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# 3. Silence ADK's model integration logs
# Note: Use 'google_adk' for the broad package or be specific as below
logging.getLogger("google_adk.models.lite_llm").setLevel(logging.WARNING)

load_dotenv()

openai_model = LiteLlm(model="openai/gpt-4o")

cpu_info_agent = Agent(
    name="cpu_info_agent",
    model=openai_model,
    instruction="""You are a CPU Information Agent.

        When asked for system information, you should:
        1. Use the 'get_cpu_info' tool to gather CPU data
        2. Analyze the returned dictionary data
        3. Format this information into a concise, clear section of a system report

        The tool will return a dictionary with:
        - result: Core CPU information
        - stats: Key statistical data about CPU usage
        - additional_info: Context about the data collection

        Format your response as a well-structured report section with:
        - CPU core information (physical vs logical)
        - CPU usage statistics
        - Any performance concerns (high usage > 80%)

        IMPORTANT: You MUST call the get_cpu_info tool. Do not make up information.
        """,
    description="Gathers and analyzes CPU information",
    tools=[get_cpu_info],
    output_key="cpu_info",
)
