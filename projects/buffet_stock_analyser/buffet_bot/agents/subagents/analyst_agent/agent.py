import logging

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .prompt import ANALYST_PROMPT

# 1. Silence Pydantic's internal validation warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)

# 2. Silence LiteLLM's verbose logs (often the biggest culprit)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# 3. Silence ADK's model integration logs
# Note: Use 'google_adk' for the broad package or be specific as below
logging.getLogger("google_adk.models.lite_llm").setLevel(logging.WARNING)

# Initializing Claude 4.6 Sonnet via LiteLlm wrapper
llm_model = LiteLlm(model="anthropic/claude-sonnet-4-6")


analyst_agent = LlmAgent(
    name="analyst_agent",
    model=llm_model,
    instruction=ANALYST_PROMPT,
    # ADK pattern: Specify which state keys this agent needs
    # input_keys=["symbol", "company_info", "raw_financials"],
    output_key="investment_reasoning",
)

# class BuffettAnalystAgent(LlmAgent):
#     def __init__(self):
#         super().__init__(
#             name="BuffettAnalyst",
#             model=llm_model,
#             instruction=ANALYST_PROMPT,
#             # ADK pattern: Specify which state keys this agent needs
#             # input_keys=["symbol", "company_info", "raw_financials"],
#             output_key="investment_reasoning",
#         )
