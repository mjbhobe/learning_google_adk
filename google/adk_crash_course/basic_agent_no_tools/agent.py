"""
00-basic-agent-no-tools.py

This is an example of a basic agent, which relies on it's pretrained knowledge to
respond to user's queries. It will NOT be able to fetch the latest info from the web
as it does not have any tools support yet! Also no session memory, so each query is
distinct and LLM has no link to previous questions or responses.

NOTE: code shared for learning purposes only! Use at your own risk.
"""

from dotenv import load_dotenv


from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from utils import load_agent_config

load_dotenv(override=True)

agent_config = load_agent_config("basic_agent")


# NOTE: ensure you have an entry for OPENAI_API_KEY in your .env file!
# also add google-adk[extensions] to your local Python environment
openai_model = LiteLlm(model="openai/gpt-4o")

openai_greeting_agent = LlmAgent(
    # NOTE: name MUST confirm to Python identifier naming rules
    name="openai_greeting_agent",
    # if you plan to use a Google LLM (for example gemini-2.5-flash), then
    # use it as below (no need to instantiate a LiteLlm instance)
    # model = "gemini-2.5-flash",  # <<<< for Google LLMs
    model=openai_model,  # <<< use a non-Google LLM
    description=agent_config["description"],
    instruction=agent_config["instruction"],
)

root_agent = openai_greeting_agent
