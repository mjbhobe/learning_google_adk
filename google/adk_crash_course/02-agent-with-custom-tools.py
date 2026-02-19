"""
02-agent-with-custom-tools.py

This example illustrates how to use an Agent with a custom tool (i.e. a function we
code and use as a tool, as compared to usig Google supplied tools such as google_search).

Components:
* Agent: The brain of the operation, defined by its instructions, tools, and the AI model it uses.
* Session: The conversation history. For this simple agent, it's just a container for a single request-response.
* Runner: The engine that connects the Agent and the Session to process your request and get a response.

NOTE: code shared for learning purposes only! Use at your own risk.
"""

import os
import asyncio
from dotenv import load_dotenv
import requests
import json
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.sessions import InMemorySessionService, Session

from utils import load_agent_config, run_agent_query

# load API keys
load_dotenv(override=True)

agent_config = load_agent_config("weather_agent")

""" Got loction co-ordinates from Google Gemini using following prompt:

List the location co-ordinates for the following locations. Return data in the following format (location name in all-lowercase)

LOCATION_COORDINATES = {
    "sunnyvale": "37.3688,-122.0363",
    ....
}

Sunnyvale, CA
San Francisco, CA
Lake Tahoe, CA
San Jose, CA
Los Angeles, CA
Seattle, WA
Redmond, WA
Portland, OR
Las Vegas, NV
Phoenix, AZ
Denver, CO
Chicago, IL
Houston, TX
Dallas, TX
Tampa, FL
Miami, FL
New York, NY
Boston, MA
Washington, DC
St Louis, MO
Atlanta, GA
London, UK
Liverpool, UK
Manchester, UK
Paris, France
Madrid, Spain
Berlin, Germany
Bonn, Germany
Frankfurt, Germany
Rome, Italy
Milan, Italy
Cairo, Egypt
Cape Town, South Africa
Johannesburg, South Africa
Durban, South Africa
Dubai, UAE
Abu Dhabi, UAE
Sharjah, UAE
Mumbai, India
Pune, India
Nashik, India
New Delhi, India
Amritsar, India
Jaipur, India
Udaipur, India
Jodhpur, India
Indore, India
Bangalore, India
Bengaluru, India
Chennai, India
Hyderabad, India
Kochi, India
Panjim, India
Margao, India
Vasco da Gama, India
Singapore, Singapore
Tokyo, Japan
Seoul, South Korea
Sydney, Australia
Perth, Australia
Melbourne, Australia
Adelaide, Australia
Christchurch, New Zealand
Wellington, New Zealand
Auckland, New Zealand
"""

LOCATION_COORDINATES = {
    "sunnyvale": "37.3688,-122.0363",
    "san francisco": "37.7749,-122.4194",
    "lake tahoe": "38.9399,-119.9772",
    "san jose": "37.3382,-121.8863",
    "los angeles": "34.0522,-118.2437",
    "seattle": "47.6062,-122.3321",
    "redmond": "47.6740,-122.1215",
    "las vegas": "36.1699,-115.1398",
    "denver": "39.7392,-104.9903",
    "chicago": "41.8781,-87.6298",
    "houston": "29.7604,-95.3698",
    "dallas": "32.7767,-96.7970",
    "tampa": "27.9506,-82.4572",
    "miami": "25.7617,-80.1918",
    "new york": "40.7128,-74.0060",
    "boston": "42.3601,-71.0589",
    "washington, dc": "38.9072,-77.0369",
    "st louis": "38.6270,-90.1994",
    "atlanta": "33.7490,-84.3880",
    "london": "51.5074,-0.1278",
    "liverpool": "53.4084,-2.9916",
    "manchester": "53.4808,-2.2426",
    "paris": "48.8566,2.3522",
    "madrid": "40.4168,-3.7038",
    "berlin": "52.5200,13.4050",
    "bonn": "50.7337,7.0998",
    "frankfurt": "50.1109,8.6821",
    "rome": "41.9028,12.4964",
    "milan": "45.4642,9.1900",
    "dubai": "25.2048,55.2708",
    "abu dhabi": "24.4539,54.3773",
    "sharjah": "25.3463,55.4209",
    "mumbai": "19.0760,72.8777",
    "new delhi": "28.6139,77.2090",
    "bangalore": "12.9716,77.5946",
    "bengaluru": "12.9716,77.5946",
    "chennai": "13.0827,80.2707",
    "hyderabad": "17.3850,78.4867",
    "panjim": "15.4909,73.8278",
    "margao": "15.2707,73.9592",
    "vasco da gama": "15.3959,73.8143",
    "singapore": "1.3521,103.8198",
    "tokyo": "35.6895,139.6917",
    "seoul": "37.5665,126.9780",
    "sydney": "-33.8688,151.2093",
    "perth": "-31.9505,115.8605",
    "melbourne": "-37.8136,144.9631",
    "adelaide": "-34.9285,138.6007",
    "christchurch": "-43.5321,172.6362",
    "wellington": "-41.2865,174.7762",
    "auckland": "-36.8485,174.7633",
}


def get_live_weather_forecast(location: str) -> dict:
    """Gets the current, real-time weather forecast for a specified location in the US.

    Args:
        location: The city name, e.g., "San Francisco".

    Returns:
        A dictionary containing the temperature and a detailed forecast.
    """
    print(f"🛠️ TOOL CALLED: get_live_weather_forecast(location='{location}')")

    # Find coordinates for the location
    normalized_location = location.lower()
    coords_str = None
    for key, val in LOCATION_COORDINATES.items():
        if key in normalized_location:
            coords_str = val
            break
    if not coords_str:
        return {
            "status": "error",
            "message": f"I don't have coordinates for {location}.",
        }

    try:
        # NWS API requires 2 steps: 1. Get the forecast URL from the coordinates.
        points_url = f"https://api.weather.gov/points/{coords_str}"
        headers = {"User-Agent": "ADK Example Application"}
        points_response = requests.get(points_url, headers=headers)
        points_response.raise_for_status()  # Raise an exception for bad status codes
        forecast_url = points_response.json()["properties"]["forecast"]

        # 2. Get the actual forecast from the URL.
        forecast_response = requests.get(forecast_url, headers=headers)
        forecast_response.raise_for_status()

        # Extract the relevant forecast details
        current_period = forecast_response.json()["properties"]["periods"][0]
        return {
            "status": "success",
            "temperature": f"{current_period['temperature']}°{current_period['temperatureUnit']}",
            "forecast": current_period["detailedForecast"],
        }
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"API request failed: {e}"}


def get_live_weather_global(location_name: str) -> dict:
    """
    Looks up coordinates for a city and fetches global weather data.
    """
    # 1. Normalize and Lookup Coordinates
    search_key = location_name.lower().strip()
    coords_str = LOCATION_COORDINATES.get(search_key)

    if not coords_str:
        return {
            "status": "error",
            "message": f"Coordinates for '{location_name}' not found.",
        }

    # 2. Parse string "lat,lon" into floats
    try:
        lat, lon = map(float, coords_str.split(","))
    except ValueError:
        return {
            "status": "error",
            "message": "Malformed coordinate string in dictionary.",
        }

    # 3. Call the Global API (Open-Meteo)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        # "current": ["temperature_2m", "relative_humidity_2m", "weather_code"],
        # Current: Real-time snapshots (comprehensive)
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "weather_code",
            "cloud_cover",
            "pressure_msl",
            "wind_speed_10m",
        ],
        # # Hourly: Next-gen details (Soil, Solar, Visibility)
        # "hourly": "temperature_2m,precipitation_probability,cloud_cover,visibility,uv_index,is_day,soil_temperature_0cm,shortwave_radiation",
        # # Daily: High-level summaries
        # "daily": "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max,daylight_duration",
        "timezone": "auto",
    }

    try:
        print(f"🛠️ TOOL CALLED: get_live_weather_global(location='{search_key}')")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        # return {
        #     "location": search_key,
        #     "status": "success",
        #     "temperature": f"{current['temperature_2m']}°C",
        #     "humidity": f"{current['relative_humidity_2m']}%",
        #     "lat_lon": f"{lat}, {lon}",
        # }

        # to return comprehensive current weather data, use following code - assuming
        # you specified all params above in the API call:
        return {
            "location": search_key,
            "status": "success",
            "temperature": f"{current['temperature_2m']}°C",
            "feels_like": f"{current['apparent_temperature']}°C",
            "humidity": f"{current['relative_humidity_2m']}%",
            "conditions": f"Code {current['weather_code']}",
            "cloud_cover": f"{current['cloud_cover']}%",
            "pressure": f"{current['pressure_msl']} hPa",
            "precipitation": f"{current['precipitation']} mm",
            "wind_speed": f"{current['wind_speed_10m']} m/s",
        }
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"API request failed: {e}"}


# Step 1 -> Create an agent
weather_agent = Agent(
    name="weather_agent",
    model=agent_config["model"],
    description=agent_config["description"],
    instruction=agent_config["instruction"],
    tools=[get_live_weather_global],
)


async def main():
    console = Console()
    session_service = InMemorySessionService()
    my_user_id = "adk_adventurer_001"

    query = ""
    while True:
        query = Prompt.ask(
            "[bright_yellow]Query (or type 'exit' or press Enter to quit): [/bright_yellow]",
            default="exit",
        )
        # query = input()
        if query.strip().lower() == "exit":
            console.print("[bright_yellow]Goodbye![/bright_yellow]")
            break

        # console.print(f"[green]🗣️ User Query:[/green] '{query}'")

        final_response = await run_agent_query(
            weather_agent,
            query,
            session_service,
            user_id=my_user_id,
        )

        console.print("[green]\n" + "-" * 50 + "\n[/green]")
        console.print("[green]🌤️ Live Weather:[/green]")
        console.print(Markdown(final_response))
        console.print("[green]\n" + "-" * 50 + "\n[/green]")


if __name__ == "__main__":
    asyncio.run(main())
