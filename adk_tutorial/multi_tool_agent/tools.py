import datetime
import httpx
import asyncio
import json

from rich.console import Console

from datetime import datetime
from zoneinfo import ZoneInfo


async def get_weather(city: str) -> dict:
    """
    Fetches real-time weather for a city using Open-Meteo's free API.
    No API keys or registration required.
    """
    # Step 1: Geocoding - Convert City Name to Coordinates
    console = Console()

    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"

    async with httpx.AsyncClient() as client:
        # Step1: get city geo location (i.e. latitude & longitude)
        geo_response = await client.get(geocoding_url)
        geo_data = geo_response.json()
        console.print(
            f"Geo-coding response: [sky_blue1]{json.dumps(geo_data, indent=2)}[sky_blue1]",
        )

        if not geo_data.get("results"):
            return {"error": f"Weather information for {city} not found!"}

        location = geo_data["results"][0]
        lat, lon = location["latitude"], location["longitude"]

        # Step2: now using open-meteo URL + lat & lon, get weather info
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m"
        )

        weather_response = await client.get(weather_url)
        weather_data = weather_response.json()
        console.print(
            f"Weather response: [sky_blue1]{json.dumps(weather_data, indent=2)}[/sky_blue1]",
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
            "city": location["name"],
            "condition": weather_desc,
            "temperature_c": weather_data["current"]["temperature_2m"],
            "humidity": weather_data["current"]["relative_humidity_2m"],
            "wind_speed": weather_data["current"]["wind_speed_10m"],
            "wind_direction": get_direction(
                weather_data["current"]["wind_direction_10m"]
            ),
        }


async def get_time(city: str) -> str:
    """
    Fetches the current local time for a city using free APIs.
    No API keys required.
    """
    # Step 1: Geocoding - Find coordinates and timezone ID
    # We use Open-Meteo's geocoding API to resolve the city name
    console = Console()
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"

    async with httpx.AsyncClient() as client:
        response = await client.get(geo_url)
        data = response.json()

        if not data.get("results"):
            return f"Error: City '{city}' not found."

        location = data["results"][0]
        timezone_id = location.get("timezone")  # e.g., "America/New_York"
        city_name = location.get("name")

        if not timezone_id:
            return f"Error: Could not determine timezone for {city_name}."

        # Step 2: Calculate local time using Python's zoneinfo
        # This uses the IANA timezone ID returned by the API
        try:
            local_tz = ZoneInfo(timezone_id)
            now_local = datetime.now(local_tz)
            console.print(
                f"Calculated local time for [sky_blue1]{city_name}[/sky_blue1] using timezone [sky_blue1]{timezone_id}[/sky_blue1]: [yellow]{now_local}[/yellow]",
            )

            # Format as 11:20 AM on 17-Feb-26
            return now_local.strftime("%I:%M %p on %d-%b-%y")
        except Exception as e:
            return f"Error calculating time: {e}"
