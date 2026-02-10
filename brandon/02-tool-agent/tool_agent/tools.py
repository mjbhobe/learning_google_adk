"""tools.py - definition of tools, such as weather tool"""

import asyncio
import python_weather
from logger_config import setup_logger  # import from our logging module

logger = setup_logger("tools")


async def _fetch_weather(location: str):
    """Internal async helper."""
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        return await client.get(location)


def get_weather(location: str) -> str:
    """
    Fetches the current weather for a specific location.

    Args:
        location: The city or place name (e.g., 'London', 'Tokyo').
    """
    logger.info(f"Weather tool called for: [bold cyan]{location}[/bold cyan]")

    try:
        data = asyncio.run(_fetch_weather(location))
        result = (
            f"Current weather in {location}: {data.temperature}°C, "
            f"{data.description}, Humidity: {data.humidity}%"
        )
        logger.info(f"[green]Successfully retrieved weather for {location}[/green]")
        return result
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        return f"Sorry, I couldn't find weather data for {location}."
