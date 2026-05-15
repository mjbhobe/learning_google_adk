"""
Code Reviewer Agent - reviews the code written by code_writer_agent

This agent is responsible for recommending appropriate next actions
based on the lead validation and scoring results.
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

load_dotenv(override=True)

openai_model = LiteLlm(model="openai/gpt-5-nano")

# NOTE: "generated_code" is the output_key of code_writer_agent
code_reviewer_agent = Agent(
    name="code_reviewer_agent",
    model=openai_model,
    instruction="""
    You are an expert Python Code Reviewer.
    Your task is to provide constructive feedback on the provided code.

    **Code to Review:**
    ```python
    {generated_code}
    ```

    **Review Criteria:**
    1.  **Correctness:** Does the code work as intended? Are there logic errors?
    2.  **Readability:** Is the code clear and easy to understand? Follows PEP 8 style guidelines?
    3.  **Efficiency:** Is the code reasonably efficient? Any obvious performance bottlenecks?
    4.  **Edge Cases:** Does the code handle potential edge cases or invalid inputs gracefully?
    5.  **Best Practices:** Does the code follow common Python best practices?
    6.  **Documentation:** Are there appropriate docstrings and comments explaining the code? 
        Docstrings should follow the Google style guide & comments must be clear & helpful and 
        not added just for the sake of commenting!

    **Output:**
    Provide your feedback as a concise, bulleted list. Focus on the most important points for 
    improvement.
    If the code is excellent and requires no changes, simply state: "No major issues found."
    Output *only* the review comments or the "No major issues found." statement.
    """,
    description="Reviews code and provides feedback.",
    output_key="review_comments",
)
