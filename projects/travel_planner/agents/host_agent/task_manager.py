"""
task_manager.py (for host agent)

executes the orchestration logic by calling remote agents and handling
the full trip-planning workflow.
"""

from rich.console import Console

from common.a2a_client import call_agent

# BAD PRACTICE: don't hard-code this into Python file
# better to externalize it into the .env file
FLIGHT_URL = "http://localhost:8001/run"
STAY_URL = "http://localhost:8002/run"
ACTIVITIES_URL = "http://localhost:8003/run"

console = Console()


async def run(payload):
    # Print what the host agent is sending
    print(f"Incoming payload: {payload}")
    flights = await call_agent(FLIGHT_URL, payload)
    stay, activities = "", ""
    # stay = await call_agent(STAY_URL, payload)
    # activities = await call_agent(ACTIVITIES_URL, payload)
    # Log outputs
    print(f"Flights: {flights}")
    # print(f"Stay: {stay}")
    # print(f"Activities: {activities}")
    # Ensure all are dicts before access
    flights = flights if isinstance(flights, dict) else {}
    stay = stay if isinstance(stay, dict) else {}
    activities = activities if isinstance(activities, dict) else {}
    return {
        "flights": flights.get("flights", "No flights returned."),
        "stay": stay.get("stays", "No stay options returned."),
        "activities": activities.get("activities", "No activities found."),
    }
