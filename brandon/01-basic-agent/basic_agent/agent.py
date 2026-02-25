from google.adk.agents import Agent

root_agent = Agent(
    name="greeting_agent",
    model="gemini-2.5-flash",
    description="Greeting agent",
    instruction="""
    You are a helpful assistant that greets the user.
    Ask for the user's name and then greet them by their name.
    Respond to any questions from your pre-trained data only as you do not have 
    access to any external tools.
    """,
)
