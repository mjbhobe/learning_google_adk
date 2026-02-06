from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="tool_agent",
    model="gemini-2.5-flash",
    description="Agent that can use tools",
    instruction="""
    You are a helpful assistant that assists the user. You can also search the 
    web for latest information using following tools:
    - google_search
    """,
    tools=[google_search],
)
