from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="tool-agent",
    model="gemini-2.0-flash",
    description="Tool agent",
    instruction="""
    You are a helpful agent that can use the following tools:
    - google_search: to search the web and retrieve information.
    """,
    tools=[google_search],
)
