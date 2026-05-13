from dotenv import load_dotenv, find_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

load_dotenv(find_dotenv(), override=True)

openai_model = LiteLlm(model="openai/gpt-5-nano")

root_agent = LlmAgent(
    name="greeting_agent",
    model=openai_model,
    description="Greeting agent",
    instruction="""
    You are a helpful assistant that greets the user with a 
    "Hi! I am the ADK Agent. How can I help you?"
    Ask for the user's name and then greet them by their name.
    Respond to any questions from your pre-trained data only as you do not have 
    access to any external tools.
    """,
)
