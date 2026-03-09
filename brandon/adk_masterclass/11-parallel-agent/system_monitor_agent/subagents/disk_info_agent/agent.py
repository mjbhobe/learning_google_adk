"""
Disk Information Agent

This agent is responsible for gathering and analyzing disk information.
"""

from dotenv import load_dotenv
import logging

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .tools import get_disk_info

# 1. Silence Pydantic's internal validation warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)

# 2. Silence LiteLLM's verbose logs (often the biggest culprit)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# 3. Silence ADK's model integration logs
# Note: Use 'google_adk' for the broad package or be specific as below
logging.getLogger("google_adk.models.lite_llm").setLevel(logging.WARNING)

load_dotenv()

openai_model = LiteLlm(model="openai/gpt-4o")

disk_info_agent = Agent(
    name="disk_info_agent",
    model=openai_model,
    instruction="""You are a Disk Information Agent.

        When asked for system information, you should:
        1. Use the 'get_disk_info' tool to gather disk data
        2. Analyze the returned dictionary data
        3. Format this information into a concise, clear section of a system report

        The tool will return a dictionary with:
        - result: Core disk information including partitions
        - stats: Key statistical data about storage usage
        - additional_info: Context about the data collection

        Format your response as a well-structured report section with:
        - Partition information
        - Storage capacity and usage
        - Any storage concerns (high usage > 85%)

        IMPORTANT: You MUST call the get_disk_info tool. Do not make up information.
        """,
    description="Gathers and analyzes disk information",
    tools=[get_disk_info],
    output_key="disk_info",
)
