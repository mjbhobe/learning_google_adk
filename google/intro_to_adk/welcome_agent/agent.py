from dotenv import load_dotenv

from google.adk.agents import Agent

root_agent = Agent(
    name="welcome_agent",
    model="gemini-3.1-flash-lite",
    description="Greeter agent",
    instruction="""
    You are a friendly assistant that greets the user and responds to their queries
  """,
)
