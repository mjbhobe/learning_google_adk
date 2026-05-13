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


"""
gemini-2.5-flash give tool calling not supported error. Here is a fix, 
as suggested by Google Gemini

from google.adk.models import Gemini # Use the Gemini wrapper

root_agent = Agent(
    name="tool_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        use_interactions_api=True  # <--- This unlocks tool calling for 2.5+
        bypass_multi_tools_limit=True  #  <---  unlocks the multi-tool restriction
    ),
    description="Agent that can use tools",
    instruction=""" """
    You are a helpful travel guide who can provide weather information.
    Use 'get_live_weather_global' to fetch weather information. For any other queries, use
    'google_search' tool to find relevant information. 
    Always provide a helpful response to the user.
    """ """,
    tools=[get_live_weather_global, google_search],
)

Can the model use both tools together?
With this setup, if a user asks: "What's the weather in London and can you find me a 
good Italian restaurant there?", the agent performs Parallel Tool Calling:

It triggers get_live_weather_global(location_name="london").

Simultaneously, it triggers Google Search(query="best Italian restaurants in London").

It merges both outputs into a single, grounded response.

Important 2026 Constraints
Billing: When using Google Search in this "mixed mode," you are billed for the model 
tokens plus a small flat fee per search query executed (if you are on a paid tier).

Vertex AI vs AI Studio: If you use an AI Studio API key, ensure your .env has GOOGLE_GENAI_USE_VERTEXAI=FALSE. If you are using Google Cloud Vertex AI, set it to TRUE.

Search Suggestions: The model will return "Search Suggestions" (chips) at the bottom of 
the response when using Google Search. The ADK handles rendering these if you are using 
the built-in adk web UI.

"""
