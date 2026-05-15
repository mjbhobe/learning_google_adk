"""
Sequential Agent example - this agent orchestrates sub-agents
    that write code, review code and re-factor code (if needed)

This example demonstrates a lead qualification pipeline with a minimal
before_agent_callback that only initializes state once at the beginning.
"""

from dotenv import load_dotenv
import logging

from google.adk.agents import SequentialAgent

# --- subagents ---
from .subagents.code_writer_agent.agent import code_writer_agent
from .subagents.code_reviewer_agent.agent import code_reviewer_agent
from .subagents.code_refactorer_agent.agent import code_refactorer_agent

# 1. Silence Pydantic's internal validation warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)

# 2. Silence LiteLLM's verbose logs (often the biggest culprit)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# 3. Silence ADK's model integration logs
# Note: Use 'google_adk' for the broad package or be specific as below
logging.getLogger("google_adk.models.lite_llm").setLevel(logging.WARNING)

load_dotenv(override=True)

root_agent = SequentialAgent(
    name="code_pipeline_agent",
    sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent],
    description="Executes a sequence of code writing, reviewing, and refactoring.",
)
