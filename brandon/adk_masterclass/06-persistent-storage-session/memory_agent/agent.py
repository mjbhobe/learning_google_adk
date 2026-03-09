from dotenv import load_dotenv
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.models import Gemini  # Use the Gemini wrapper
from google.adk.tools import google_search

from .logger import get_logger

APP_NAME = Path(__file__).parent.resolve().name

load_dotenv(override=True)
logger = get_logger(f"{APP_NAME}.agent")

gemini_model = Gemini(
    model="gemini-2.5-flash",
    use_interactions_api=True,  # <--- This unlocks tool calling for 2.5+
    bypass_multi_tools_limit=True,  #  <---  unlocks the multi-tool restriction
    # however, you STILL cannot mix internal tools (such as google_search) with
    # your own custom tools!
)

# uncomment following line & change gemini_model to openai_model
# in agent definition if you want to use OpenAI LLM
# openai_model = LiteLlm(model="openai/gpt-4o")

root_agent = LlmAgent(
    # A bot that tells you all you need to know about Manish.
    name="manu_bot",
    model=gemini_model,
    # NOTE: any variables within {} are automatically resolved from the session
    # state - for example user_name would be resolved from session.get("user_name")
    instruction="""
        You are a helpful assistant that answers questions about the user's preferences.

        Here is some information about the user:
        Name: 
        {user_name}
        Preferences: 
        {user_preferences}
    """,
    description="Q&A Agent on user preferences",
)


"""
gemini-2.5-flash give tool calling not supported error. Here is a fix, 
as suggested by Google Gemini App

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

How the Model Uses Both
With this setup, if a user asks: "What's the weather in London and can you 
find me a good Italian restaurant there?", the agent performs Parallel Tool Calling:

It triggers get_live_weather_global(location_name="london").

Simultaneously, it triggers Google Search(query="best Italian restaurants in London").

It merges both outputs into a single, grounded response.

Important 2026 Constraints
Billing: When using Google Search in this "mixed mode," you are billed for the model tokens plus a small flat fee per search query executed (if you are on a paid tier).

Vertex AI vs AI Studio: If you use an AI Studio API key, ensure your .env has GOOGLE_GENAI_USE_VERTEXAI=FALSE. If you are using Google Cloud Vertex AI, set it to TRUE.

Search Suggestions: The model will return "Search Suggestions" (chips) at the bottom of the 
response when using Google Search. The ADK handles rendering these if you are using the 
built-in adk web UI.
"""
