from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from datetime import datetime
from zoneinfo import ZoneInfo

CITY_TIMEZONE_MAP = {
    "New York": "America/New_York",
    "Los Angeles": "America/Los_Angeles",
    "Chicago": "America/Chicago",
    "Houston": "America/Chicago",
    "Phoenix": "America/Phoenix",
    "Philadelphia": "America/New_York",
    "San Antonio": "America/Chicago",
    "San Diego": "America/Los_Angeles",
    "Dallas": "America/Chicago",
    "San Jose": "America/Los_Angeles",
    "London": "Europe/London",
    "Paris": "Europe/Paris",
    "Berlin": "Europe/Berlin",
    "Moscow": "Europe/Moscow",
    "Dubai": "Asia/Dubai",
    "New Delhi": "Asia/Kolkata",
    "Mumbai": "Asia/Kolkata",
    "Bengaluru": "Asia/Kolkata",
    "Kolkata": "Asia/Kolkata",
    "Chennai": "Asia/Kolkata",
    "Hyderabad": "Asia/Kolkata",
    "Bangkok": "Asia/Bangkok",
    "Tokyo": "Asia/Tokyo",
    "Sydney": "Australia/Sydney",
}


def get_current_time(city: str) -> dict:
    """Get the current time in a city."""
    # convert city name to title case (e.g., san Francisco -> San Francisco)
    city = city.title()
    if city not in CITY_TIMEZONE_MAP:
        return {"error": "Sorry, I don't know the time in {}.".format(city)}
    else:
        timezone = ZoneInfo(CITY_TIMEZONE_MAP[city])
        current_time = datetime.now(timezone)
        return {
            "status": "success",
            "city": city,
            "time": current_time.strftime("%H:%M:%S"),
        }


root_agent = Agent(
    name="root_agent",
    model="gemini-1.5-flash",
    description="Tells the current time in a city.",
    instruction="""
    You are a helpful assistant that can answer questions, search the web 
    also tell time in a city. For this you can leverage the following tools:
    - google_search
    - get_current_time
    """,
    tools=[get_current_time, google_search],
)
