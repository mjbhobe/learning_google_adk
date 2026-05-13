from dotenv import load_dotenv, find_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

load_dotenv(find_dotenv(), override=True)

# NOTE: I am attempting to use the cheapest models from
# each provider. You can change it to whichever model you'd like to use

# for OpenAI LLM use following line
model = LiteLlm(model="openai/gpt-5-nano")
# for Google Gemini use this instead (using 3.1 flash lite)
# model = LiteLlm(model="gemini/gemini-3.1-flash-lite")
# for Anthropic Claude Haiku use
# model = LiteLlm(model="anthropic/claude-4-5-haiku")

root_agent = LlmAgent(
    name="greeting_agent",
    model=model,
    description="Greeting agent",
    instruction="""
    You are a helpful assistant that greets the user with a 
    "Hi! I am the ADK Agent. How can I help you?"
    Ask for the user's name and then greet them by their name.
    Respond to any questions from your pre-trained data only as you do not have 
    access to any external tools.
    """,
)
