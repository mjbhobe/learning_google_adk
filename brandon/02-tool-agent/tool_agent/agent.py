from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.runners import InMemoryRunner
from google.genai import types

from tools import get_weather
from logger_config import setup_logger

load_dotenv(override=True)
# Initialize agent-level logger
logger = setup_logger("agent")


root_agent = Agent(
    name="tool_agent",
    model="gemini-2.5-flash",
    description="Agent that can use tools",
    instruction="""
    You are a helpful travel guide who can provide weather information.
    Use 'get_weather' to fetch weather information. For any other queries, use
    'google_search' tool to find relevant information. 
    Always provide a helpful response to the user.
    """,
    tools=[get_weather, google_search],
)

if __name__ == "__main__":
    runner = InMemoryRunner(agent=root_agent)

    # query = "Tell me places to visit in London."
    query = "What's the weather like in London today?"
    logger.info(f"Processing user query: [yellow]{query}[/yellow]")

    # 3. Format the input for the ADK Runner
    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=query)],
    )

    # 4. Execute using the runner
    # Note: InMemoryRunner.run returns a generator of events
    events = runner.run(
        user_id="local_user",
        session_id="session_123",
        new_message=user_content,
    )

    # 5. Extract and print the final response
    for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                # The final response is usually the last text part
                print(
                    f"\n[bold green]Agent Response:[/bold green]\n{event.content.parts[0].text}"
                )
