from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

openai_model = LiteLlm(model="openai/gpt-4o")

root_agent = LlmAgent(
    name="greeting_agent",
    model=openai_model,
    description="Greeting agent",
    instruction="""
    You are a helpful assistant that greets the user with a "Hi! I am the ADK Agent. How can I help you?"
    Ask for the user's name and then greet them by their name.
    Respond to any questions from your pre-trained data only as you do not have 
    access to any external tools.
    """,
)
