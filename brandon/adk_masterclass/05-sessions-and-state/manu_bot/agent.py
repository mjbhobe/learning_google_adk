from dotenv import load_dotenv
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .logger import get_logger

load_dotenv(override=True)
# Initialize agent-level logger
logger = get_logger("sessions_and_memory.agent")

# NOTE: I am attempting to use the cheapest models from
# each provider. You can change it to whichever model you'd like to use

# for OpenAI LLM use following line
model = LiteLlm(model="openai/gpt-5-nano")
# for Google Gemini use this instead (using 3.1 flash lite)
# model = LiteLlm(model="gemini/gemini-3.1-flash-lite")
# for Anthropic Claude Haiku use
# model = LiteLlm(model="anthropic/claude-4-5-haiku")

root_agent = LlmAgent(
    # A bot that tells you all you need to know about Manish.
    name="manu_bot",
    model=model,
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
