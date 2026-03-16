import os
from dotenv import load_dotenv
import textwrap
from datetime import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from google.adk.models.google_llm import Gemini

load_dotenv(override=True)
assert os.getenv("GOOGLE_API_KEY") is not None, "FATAL: GOOGLE_API_KEY is not set"


llm = Gemini(
    model="gemini-3-flash-preview",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
    top_p=0.95,
    top_k=40,
    max_output_tokens=2048,
    stream=True,
)

PROMPT = """
You are a helpful assistant that answers user's questions.
Start with a cheerful greeting and ask the user name and then ask 
what you can help the user with.
Keep your responses brief and too the point, don't provide any extra information.
You have access to the following tools:
- google_search: Use this tool to search the web for information.
ALWAYS use the tools to find information & do not answer from your 
pretrained data even if you know the answer!
If you are unable to answer the question, respond with a polite message
such as "Sorry, I am unable to respond to that question". Do not wing it!
"""

root_agent = LlmAgent(
    name="agent_with_internal_tools",
    model=llm,
    description="A helpful agent that answers user's questions",
    instruction=textwrap.dedent(PROMPT).strip(),
    tools=[google_search],
)
