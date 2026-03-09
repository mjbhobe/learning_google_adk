import asyncio
from datetime import datetime
from typing import Any
from rich.console import Console

from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai import types

from logger import get_logger

console = Console()
logger = get_logger("customer_service_agent.utils")


async def update_interaction_history(
    session: Session,
    entry: dict[str, Any],
):
    """Add an entry to the interaction history in state.

    Args:
        session: the session instance shared between agents
        entry: A dictionary containing the interaction data
            - requires 'action' key (e.g., 'user_query', 'agent_response')
            - other keys are flexible depending on the action type
    """
    try:
        # Get current interaction history
        interaction_history = session.state.get("interaction_history", [])

        # Add timestamp if not already present
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the entry to interaction history
        interaction_history.append(entry)

        logger.info(
            f"update_interaction_history() -> Interaction history: {interaction_history}"
        )

        # update the session state
        session.state["interaction_history"] = interaction_history
    except Exception as e:
        print(f"Error updating interaction history: {e}")


async def add_user_query_to_history(
    session: Session,
    query: str,
):
    """Add a user query to the interaction history."""
    await update_interaction_history(
        session,
        {
            "action": "user_query",
            "query": query,
        },
    )


async def add_agent_response_to_history(
    session: Session,
    agent_name: str,
    response: str,
):
    """Add an agent response to the interaction history."""
    await update_interaction_history(
        session,
        {
            "action": "agent_response",
            "agent": agent_name,
            "response": response,
        },
    )


async def display_state(
    # session_service, app_name, user_id, session_id, label="Current State"
    session: Session,
    label: str = "Current State",
):
    """Display the current session state in a formatted way."""
    try:
        # Format the output with clear sections
        print(f"\n{'-' * 10} {label} {'-' * 10}")

        # Handle the user name
        user_name = session.state.get("user_name", "Unknown")
        print(f"👤 User: {user_name}")

        # Handle purchased courses
        purchased_courses = session.state.get("purchased_courses", [])
        if purchased_courses and any(purchased_courses):
            print("📚 Courses:")
            for course in purchased_courses:
                if isinstance(course, dict):
                    course_id = course.get("id", "Unknown")
                    purchase_date = course.get("purchase_date", "Unknown date")
                    print(f"  - {course_id} (purchased on {purchase_date})")
                elif course:  # Handle string format for backward compatibility
                    print(f"  - {course}")
        else:
            print("📚 Courses: None")

        # Handle interaction history in a more readable way
        interaction_history = session.state.get("interaction_history", [])
        if interaction_history:
            print("📝 Interaction History:")
            for idx, interaction in enumerate(interaction_history, 1):
                # Pretty format dict entries, or just show strings
                if isinstance(interaction, dict):
                    action = interaction.get("action", "interaction")
                    timestamp = interaction.get("timestamp", "unknown time")

                    if action == "user_query":
                        query = interaction.get("query", "")
                        print(f'  {idx}. User query at {timestamp}: "{query}"')
                    elif action == "agent_response":
                        agent = interaction.get("agent", "unknown")
                        response = interaction.get("response", "")
                        # Truncate very long responses for display
                        if len(response) > 100:
                            response = response[:97] + "..."
                        print(f'  {idx}. {agent} response at {timestamp}: "{response}"')
                    else:
                        details = ", ".join(
                            f"{k}: {v}"
                            for k, v in interaction.items()
                            if k not in ["action", "timestamp"]
                        )
                        print(
                            f"  {idx}. {action} at {timestamp}"
                            + (f" ({details})" if details else "")
                        )
                else:
                    print(f"  {idx}. {interaction}")
        else:
            print("📝 Interaction History: None")

        # Show any additional state keys that might exist
        other_keys = [
            k
            for k in session.state.keys()
            if k not in ["user_name", "purchased_courses", "interaction_history"]
        ]
        if other_keys:
            print("🔑 Additional State:")
            for key in other_keys:
                print(f"  {key}: {session.state[key]}")

        print("-" * (22 + len(label)))
    except Exception as e:
        print(f"Error displaying state: {e}")


async def process_agent_response(event):
    """Process and display agent response events."""
    logger.info(
        f"process_agent_response() -> Event ID: {event.id}, Author: {event.author}"
    )

    # Check for specific parts first
    has_specific_part = False
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text and not part.text.isspace():
                logger.info(f"  Text: '{part.text.strip()}'")

    # Check for final response after specific parts
    final_response = None
    if not has_specific_part and event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            # Use colors and formatting to make the final response stand out
            console.print(
                f"\n[bold blue]╔══ AGENT RESPONSE ═════════════════════════════════════════[/bold blue]"
            )
            console.print(f"[bold_cyan]{final_response}[/bold_cyan]")
            console.print(
                f"[bold blue]╚═════════════════════════════════════════════════════════════[/bold blue]\n"
            )
        else:
            console.print(
                f"\n[bold_red]==> Final Agent Response: [No text content in final event][bold_red]\n"
            )

    return final_response


async def call_agent_async(
    runner, session: Session, user_id: str, session_id: str, query: str
):
    """Call the agent asynchronously with the user's query."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    console.print(f"\n[bold_green]--- Running Query: {query} ---[/bold_green]")
    final_response_text = None
    agent_name = None

    # # Display state before processing the message
    # await display_state(
    #     runner.session_service,
    #     runner.app_name,
    #     user_id,
    #     session_id,
    #     "State BEFORE processing",
    # )

    # Display state before processing the message
    await display_state(
        session,
        "State BEFORE processing",
    )

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # Capture the agent name from the event if available
            if event.author:
                agent_name = event.author

            response = await process_agent_response(event)
            if response:
                final_response_text = response

            if final_response_text and agent_name:
                logger.info(
                    f"call_agent_async() -> \n   Final response text: {final_response_text}\n   Agent Name: {agent_name}"
                )
    except Exception as e:
        console.print(f"[dark_red]ERROR during agent run: {e}[/dark_red]")

    # Add the agent response to interaction history if we got a final response
    logger.info(
        f"call_agent_async() -> AFTER try block\n   Final response text: {final_response_text}\n   Agent Name: {agent_name}"
    )
    if final_response_text and agent_name:
        await add_agent_response_to_history(
            session,
            agent_name,
            final_response_text,
        )

    # Display state after processing the message
    await display_state(
        session,
        "State AFTER processing",
    )

    console.print(f"[yellow]{'-' * 30}[/yellow]")
    return final_response_text
