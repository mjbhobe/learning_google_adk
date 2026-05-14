"""
Google ADK Agent that works with tools

In this example, we power our agent with the OpenAI gpt-5-nano LLM
and 2 custom built tools:
  - get_live_weather_global - that gets weather from most global cities
  - web_search - custom web serach using Tavily API

NOTE: Google ADK does NOT support using Google tools (such as google_search)
with non-Google LLMs. So if you want to use google_search, instead of web_serach,
use a Google Gemini LLM (such as gemini-2.5-flash). API access used to be free (&
pretty generous until recently, when the quotas are very restricted!)

@Author: Manish Bhobé
My experiments with AI/Gen AI. Code shared for learning purposes only.
Use at your own risk!!
"""

from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.models import Gemini  # Use the Gemini wrapper
from google.adk.tools import google_search

from tool_agent.tools import get_live_weather_global, web_search
from tool_agent.logger import get_logger

load_dotenv(override=True)
# Initialize agent-level logger
logger = get_logger("tool_agent.agent")

# NOTE: I am attempting to use the cheapest models from
# each provider. You can change it to whichever model you'd like to use

# for OpenAI LLM use following line
model = LiteLlm(model="openai/gpt-5-nano")
# for Google Gemini use this instead (using 3.1 flash lite)
# model = LiteLlm(model="gemini/gemini-3.1-flash-lite")
# for Anthropic Claude Haiku use
# model = LiteLlm(model="anthropic/claude-4-5-haiku")

root_agent = Agent(
    name="tool_agent",
    model=model,
    description="Agent that can use tools",
    instruction="""
    You are a helpful travel guide who can provide weather information.
    Use 'get_live_weather_global' to fetch weather information. For any other queries, use
    'web_search' tool to find relevant information.
    Always provide a helpful response to the user and don't add extra text to your response,
    such as suggestions or what else you can do. Just answer the question(s) from user.
    Use a casual and helpful tone in your response.
    """,
    # NOTE: OpenAI models CANNOT use Google tools, like google_search
    # hence we have created custom tools for web-search using Tavily API
    tools=[get_live_weather_global, web_search],
)


# A note regarding using Google tools along with custom tools in an Agent.

# 1. Firstly, to use Google tooks, such as google_search (google.adk.tools.google_search)
#    you MUST use a Gemini model that supports tool use, such as gemini-2.5-flash or above.
#    The "flash" models are the ones that support tool use (gemini-2.5-flash,
#    gemini-3.1-flash, etc.)

# 2. ADK does NOT allow you to use additional tools with any google tools (such as google_search).
#    So if you want to use google_search, you cannot use any other tools in the same agent,
#    even when you are using Gemini LLMs.

# However, as of Mar 2026, Google introduces the "Interactions API & Tool Context Circulation"
# in the ADK. This is a very fancy name, but what it allows you to do is to use Google tools
# (such as google_search) along with custom tools in the same agent. This is a game changer
# in the ADK.

# To use this feature, you need to set `use_interactions_api=True` and
# `bypass_multi_tools_limit=True` in the Gemini wrapper when initializing the agent model,
# as shown below:

# Here are the changes you'll have to make to the agent above
# (NOTE the inline comments preceeded by <--- )

# from dotenv import load_dotenv

# from google.adk.agents import Agent
# # <---  don't use LiteLLM
# # from google.adk.models.lite_llm import LiteLlm
# # <---  use the Gemini wrapper instead
# from google.adk.models import Gemini
# from google.adk.tools import google_search

# from tool_agent.tools import get_live_weather_global  # , web_search  # <---  don't need web_search tool
# from tool_agent.logger import get_logger

# load_dotenv(override=True)
# # Initialize agent-level logger
# logger = get_logger("tool_agent.agent")

# # NOTE: <---  instantiate your Gemini flash LLM like this
# gemini_model = Gemini(
#     model="gemini-3.1-flash-lite",  # or any flash model, such as gemini-2.5-flash
#     use_interactions_api=True,  # <--- This unlocks tool calling for 2.5+
#     bypass_multi_tools_limit=True,  #  <---  unlocks the multi-tool restriction
# )

# root_agent = Agent(
#     name="tool_agent",
#     model=gemini_model,  # <--- use the Gemini wrapper instance here,
#     description="Agent that can use tools",
#     instruction="""
#     You are a helpful travel guide who can provide weather information.
#     Use 'get_live_weather_global' to fetch weather information. For any other queries, use
#     'web_search' tool to find relevant information.
#     Always provide a helpful response to the user and don't add extra text to your response,
#     such as suggestions or what else you can do. Just answer the question(s) from user.
#     Use a casual and helpful tone in your response.
#     """,
#     # NOTE: <--- now you can use multiple tools, including google tools
#     tools=[get_live_weather_global, google_search],
# )
