from dotenv import load_dotenv
from google.adk.agents import Agent
from google.genai import types

load_dotenv(override=True)

root_agent = Agent(
    # the value of name must follow Python variable naming conventions
    name="welcome_agent",
    model="gemini-3.1-flash-lite-preview",
    description="Greeting agent that greets the user",
    instruction="You are a helpful assistant that greets the user in a friendly tone",
)
