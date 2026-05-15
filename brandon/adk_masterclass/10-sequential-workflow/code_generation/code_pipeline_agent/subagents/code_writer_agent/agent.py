"""
Code Writer agent - writes the Python code depending on user's requirements

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

code_writer_agent = Agent(
    name="code_writer_agent",
    model=openai_model,
    instruction="""
    You are a Python Code Generator.
    Based *only* on the user's request, write Python code that fulfills the requirement.
    Ensure that the code meets PEP 8 style guidelines and includes appropriate docstrings 
    (Google style) and comments for clarity - do not add comments for the sake of commenting, 
    comments must be clear and helpful!
    Output *only* the complete Python code block with comments & docstrings, enclosed in 
    triple backticks (```python ... ```).
    Do not add any other text before or after the code block.
    """,
    description="Writes initial Python code based on a specification.",
    output_key="generated_code",
)
