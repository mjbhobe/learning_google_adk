import os
from dotenv import load_dotenv
import textwrap

from google.adk.agents import LlmAgent

from google.adk.models.google_llm import Gemini

load_dotenv(override=True)
assert os.getenv("GOOGLE_API_KEY") is not None, "FATAL: GOOGLE_API_KEY is not set"


llm = Gemini(
    model="gemini-2.5-flash",
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
Keep your responses brief and too the point, don't provide too much 
information.
If you are unable to answer the question, respond with a polite message
such as "Sorry, I am unable to respond to that question". Do not wing it!
"""

root_agent = LlmAgent(
    name="my_first_agent",
    model=llm,
    description="A helpful agent that answers user's questions",
    instruction=textwrap.dedent(PROMPT).strip(),
)
