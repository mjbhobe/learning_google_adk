import logging

from google.adk.agents import SequentialAgent

from .subagents.analyst_agent.agent import analyst_agent
from .subagents.reporter_agent.agent import reporter_agent

# 1. Silence Pydantic's internal validation warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)

# 2. Silence LiteLLM's verbose logs (often the biggest culprit)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# 3. Silence ADK's model integration logs
# Note: Use 'google_adk' for the broad package or be specific as below
logging.getLogger("google_adk.models.lite_llm").setLevel(logging.WARNING)


root_agent = SequentialAgent(
    name="buffett_stock_analysis_workflow",
    # NOTE: we do NOT require a model for this type agent!
    # but we DO need to define sub-agents, which will run "left-to-right"
    sub_agents=[analyst_agent, reporter_agent],
    description="A pipeline that analyses raw financial metrics of stock and generates recommendation & a structured report",
)
