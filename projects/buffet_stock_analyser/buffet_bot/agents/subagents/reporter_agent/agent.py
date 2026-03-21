import logging

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .prompt import REPORTER_PROMPT

# 1. Silence Pydantic's internal validation warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)

# 2. Silence LiteLLM's verbose logs (often the biggest culprit)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# 3. Silence ADK's model integration logs
# Note: Use 'google_adk' for the broad package or be specific as below
logging.getLogger("google_adk.models.lite_llm").setLevel(logging.WARNING)

llm_model = LiteLlm(model="anthropic/claude-sonnet-4-6")

reporter_agent = LlmAgent(
    name="reporter_agent",
    model=llm_model,
    instruction=REPORTER_PROMPT,
    output_key="final_markdown_report",
)


# class MarkdownReporterAgent(LlmAgent):
#     def __init__(self):
#         super().__init__(
#             name="MarkdownReporter",
#             model=llm_model,
#             instruction=REPORTER_PROMPT,
#             input_keys=[
#                 "symbol",
#                 "company_info",
#                 "raw_financials",
#                 "investment_reasoning",
#             ],
#             output_key="final_markdown_report",
#         )
