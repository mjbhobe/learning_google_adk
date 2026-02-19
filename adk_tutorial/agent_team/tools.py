import httpx
import json
from typing import Optional
from rich.console import Console

from google.adk.tools.tool_context import ToolContext

from logger import get_logger

logger = get_logger("agent_team.tools")


async def get_weather(city: str, tool_context: ToolContext) -> dict:
    """
    Retrieves the current weather report for a specified city.
    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
                Includes a 'status' key ('success' or 'error').
                If 'success', includes additional keys under "weather_info" key
                with with weather details, such as condition, temperature, humidity,
                wind speed, and wind direction.
                If 'error', includes an 'error_message' key.
    """
    # Step 1: Geocoding - Convert City Name to Coordinates
    console = Console()
    logger.info(f"get_weather tool called with city: {city}")

    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"

    async with httpx.AsyncClient() as client:
        # Step1: get city geo location (i.e. latitude & longitude)
        geo_response = await client.get(geocoding_url)
        geo_data = geo_response.json()
        logger.debug(
            f"Geo-coding response: {json.dumps(geo_data, indent=2)}",
        )

        if not geo_data.get("results"):
            logger.error(f"Geocoding failed for city: {city}. No results found.")
            return {
                "status": "error",
                "error_message": f"Weather information for {city} not found!",
            }

        location = geo_data["results"][0]
        lat, lon = location["latitude"], location["longitude"]
        logger.info(
            f"Geocoding successful for city: {city}. Latitude: {lat}, Longitude: {lon}"
        )

        # Step2: now using open-meteo URL + lat & lon, get weather info
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m"
        )

        weather_response = await client.get(weather_url)
        weather_data = weather_response.json()
        logger.debug(
            f"Weather response: {json.dumps(weather_data, indent=2)}",
        )

        # return {
        #     "city": location["name"],
        #     "country": location.get("country"),
        #     "temperature_c": weather_data["current"]["temperature_2m"],
        #     "humidity": weather_data["current"]["relative_humidity_2m"],
        #     "wind_speed": weather_data["current"]["wind_speed_10m"],
        #     "coordinates": {"lat": lat, "lon": lon},
        # }

        # Helper to map weather code to text (Simplified example)

        description_map = {
            0: "Sunny",
            1: "Mainly Clear",
            2: "Partly Cloudy",
            3: "Overcast",
        }
        weather_desc = description_map.get(
            weather_data["current"]["weather_code"], "Cloudy"
        )

        # Helper to map degrees to compass
        def get_direction(deg):
            directions = [
                "North",
                "North East",
                "East",
                "South East",
                "South",
                "South West",
                "West",
                "North West",
            ]
            return directions[int((deg + 22.5) % 360 / 45)]

        return {
            "status": "success",
            "weather_info": {
                "city": location["name"],
                "condition": weather_desc,
                "temperature_c": weather_data["current"]["temperature_2m"],
                "humidity": weather_data["current"]["relative_humidity_2m"],
                "wind_speed": weather_data["current"]["wind_speed_10m"],
                "wind_direction": get_direction(
                    weather_data["current"]["wind_direction_10m"]
                ),
            },
        }


def say_hello(name: Optional[str] = None) -> str:
    """A simple tool that returns a greeting message.

    Args:
        name (str, optional): The name of the person to greet. Defaults to None.

    Returns:
        str: A greeting message.
    """
    logger.info(f"say_hello tool called with name: {name}")
    if name:
        return f"Hello, {name}! Nice to meet you!"
    else:
        return "Hello World 😀! Nice to meet you!"


def say_goodbye(name: Optional[str] = None) -> str:
    """A simple tool that returns a goodbye message.

    Args:
        name (str, optional): The name of the person to say goodbye to. Defaults to None.

    Returns:
        str: A goodbye message.
    """
    logger.info(f"say_goodbye tool called with name: {name}")
    if name:
        return f"Goodbye, {name}! It was nice meeting you!"
    else:
        return "Goodbye cruel world 😢! It was nice meeting you!"
