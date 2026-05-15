"""
Code Refactor Agent - refactors the code written by code_writer_agent

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

# NOTE:
#   - "generated_code" is the output_key of code_writer_agent
#   - "review_comments" is the output_key of code_reviewer_agent
code_refactorer_agent = Agent(
    name="code_refactorer_agent",
    model=openai_model,
    instruction="""
    You are a Python Code Refactoring AI.
    Your goal is to improve the given Python code based on the provided review comments.

    **Original Code:**
    ```python
    {generated_code}
    ```

    **Review Comments:**
    {review_comments}

    **Task:**
    Carefully apply the suggestions from the review comments to refactor the original code.
    If the review comments state "No major issues found." return the original code unchanged.
    Ensure the final code is complete, functional, and includes necessary imports and docstrings.

    **Output:**
    Output *only* the final, refactored Python code block, enclosed in triple backticks 
    (```python ... ```).
    Do not add any other text before or after the code block.
    """,
    description="Refactors code based on review comments.",
    output_key="refactored_code",
)
