"""tools.py - definition of tools, such as weather tool"""

import os
from dotenv import load_dotenv
import asyncio
import requests
import httpx
from logger import get_logger

load_dotenv(override=True)
logger = get_logger("tool_agent.tools")


""" Got loction co-ordinates from Google Gemini using following prompt:

List the location co-ordinates for the following locations. Return data in the following format (location name in all-lowercase)

LOCATION_COORDINATES = {
    "sunnyvale": "37.3688,-122.0363",
    ....
}

Honolulu, HI
Anchorage, AK
Seattle, WA
Redmond, WA
Portland, OR
Sunnyvale, CA
San Francisco, CA
San Jose, CA
Lake Tahoe, CA
Los Angeles, CA
San Diego, CA
Las Vegas, NV
Phoenix, AZ
Tucson, AZ
Salt Lake City, UT
Denver, CO
Albuquerque, NM
Houston, TX
Dallas, TX
San Antonio, TX
Austin, TX
New Orleans, LA
Memphis, TN
Nashville, TN
Atlanta, GA
Augusta, GA
Savannah, GA
Tampa, FL
Miami, FL
Orlando, FL
Charlotte, NC
St Louis, MO
Louisville, KY
Indianapolis, IN
Chicago, IL
Milwaukee, WI
Minneapolis, MN
Detroit, MI
Cleveland, OH
Cincinnati, OH
Columbus, OH
Washington, DC
Baltimore, MD
Pittsburgh, PA
Philadelphia, PA
Allentown, PA
Hershey, PA
Richmond, VA
New York, NY
Newark, NJ
New Haven, CT
Newport, RI
Providence, RI
Boston, MA
Worcester, MA
Toronto, Canada
Montreal, Canada
Ottawa, Canada
Vancouver, Canada
Quebec City, Canada
Winnipeg, Canada
Calgary, Canada
Edmonton, Canada
London, UK
Liverpool, UK
Manchester, UK
Birmingham, UK
Oxford, UK
Cambridge, UK
Leeds, UK
Edinburgh, UK
Glasgow, UK
Belfast, UK
Dublin, Ireland
Amsterdam, Netherlands
Rotterdam, Netherlands
Brussels, Belgium
Antwerp, Belgium
Paris, France
Marseille, France
Bordeaux, France
Madrid, Spain
Barcelona, Spain
Lisbon, Portugal
Porto, Portugal
Zurich, Switzerland
Basel, Switzerland
Geneva, Switzerland
Rome, Italy
Milan, Italy
Venice, Italy
Florence, Italy
Berlin, Germany
Bonn, Germany
Frankfurt, Germany
Hamburg, Germany
Munich, Germany
Stuttgart, Germany
Warsaw, Poland
Krakow, Poland
Moscow, Russia
Saint Petersburg, Russia
Kiev, Ukraine
Odessa, Ukraine
Istanbul, Turkey
Jerusalem, Israel
Tel Aviv, Israel
Cairo, Egypt
Riyadh, Saudi Arabia
Dubai, UAE
Abu Dhabi, UAE
Sharjah, UAE
Cape Town, South Africa
Johannesburg, South Africa
Durban, South Africa
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
Bangkok, Thailand
Ho Chi Minh City, Vietnam
Manila, Philippines
Kuala Lumpur, Malaysia
Jakarta, Indonesia
Shanghai, China
Beijing, China
Taipai, Taiwan
Tokyo, Japan
Osaka, Japan
Seoul, South Korea
Perth, Australia
Adelaide, Australia
Melbourne, Australia
Sydney, Australia
Brisbane, Australia
Hobart, Australia
Christchurch, New Zealand
Wellington, New Zealand
Auckland, New Zealand
"""

LOCATION_COORDINATES = {
    "honolulu": "21.3069,-157.8583",
    "anchorage": "61.2181,-149.9003",
    "seattle": "47.6062,-122.3321",
    "redmond": "47.6740,-122.1215",
    "portland": "45.5152,-122.6784",
    "sunnyvale": "37.3688,-122.0363",
    "san francisco": "37.7749,-122.4194",
    "san jose": "37.3382,-121.8863",
    "lake tahoe": "39.0968,-120.0324",
    "los angeles": "34.0522,-118.2437",
    "san diego": "32.7157,-117.1611",
    "las vegas": "36.1699,-115.1398",
    "phoenix": "33.4484,-112.0740",
    "tucson": "32.2226,-110.9747",
    "salt lake city": "40.7608,-111.8910",
    "denver": "39.7392,-104.9903",
    "albuquerque": "35.0844,-106.6504",
    "houston": "29.7604,-95.3698",
    "dallas": "32.7767,-96.7970",
    "san antonio": "29.4241,-98.4936",
    "austin": "30.2672,-97.7431",
    "new orleans": "29.9511,-90.0715",
    "memphis": "35.1495,-90.0490",
    "nashville": "36.1627,-86.7816",
    "atlanta": "33.7490,-84.3880",
    "augusta": "33.4735,-82.0105",
    "savannah": "32.0809,-81.0912",
    "tampa": "27.9506,-82.4572",
    "miami": "25.7617,-80.1918",
    "orlando": "28.5383,-81.3792",
    "charlotte": "35.2271,-80.8431",
    "st louis": "38.6270,-90.1994",
    "louisville": "38.2527,-85.7585",
    "indianapolis": "39.7684,-86.1581",
    "chicago": "41.8781,-87.6298",
    "milwaukee": "43.0389,-87.9065",
    "minneapolis": "44.9778,-93.2650",
    "detroit": "42.3314,-83.0458",
    "cleveland": "41.4993,-81.6944",
    "cincinnati": "39.1031,-84.5120",
    "columbus": "39.9612,-82.9988",
    "washington, dc": "38.9072,-77.0369",
    "baltimore": "39.2904,-76.6122",
    "pittsburgh": "40.4406,-79.9959",
    "philadelphia": "39.9526,-75.1652",
    "allentown": "40.6023,-75.4714",
    "hershey": "40.2859,-76.6502",
    "richmond": "37.5407,-77.4360",
    "new york": "40.7128,-74.0060",
    "newark": "40.7357,-74.1724",
    "new haven": "41.3083,-72.9279",
    "newport": "41.4901,-71.3128",
    "providence": "41.8240,-71.4128",
    "boston": "42.3601,-71.0589",
    "worcester": "42.2626,-71.8023",
    "toronto": "43.6532,-79.3832",
    "montreal": "45.5017,-73.5673",
    "ottawa": "45.4215,-75.6972",
    "vancouver": "49.2827,-123.1207",
    "quebec city": "46.8139,-71.2080",
    "winnipeg": "49.8951,-97.1384",
    "calgary": "51.0447,-114.0719",
    "edmonton": "53.5461,-113.4938",
    "london": "51.5074,-0.1278",
    "liverpool": "53.4084,-2.9916",
    "manchester": "53.4808,-2.2426",
    "birmingham": "52.4862,-1.8904",
    "oxford": "51.7520,-1.2577",
    "cambridge": "52.2053,0.1218",
    "leeds": "53.8008,-1.5491",
    "edinburgh": "55.9533,-3.1883",
    "glasgow": "55.8642,-4.2518",
    "belfast": "54.5973,-5.9301",
    "dublin": "53.3498,-6.2603",
    "amsterdam": "52.3676,4.9041",
    "rotterdam": "51.9225,4.4792",
    "brussels": "50.8503,4.3517",
    "antwerp": "51.2194,4.4025",
    "paris": "48.8566,2.3522",
    "marseille": "43.2965,5.3698",
    "bordeaux": "44.8378,-0.5792",
    "madrid": "40.4168,-3.7038",
    "barcelona": "41.3851,2.1734",
    "lisbon": "38.7223,-9.1393",
    "porto": "41.1579,-8.6291",
    "zurich": "47.3769,8.5417",
    "basel": "47.5596,7.5886",
    "geneva": "46.2044,6.1432",
    "rome": "41.9028,12.4964",
    "milan": "45.4642,9.1900",
    "venice": "45.4408,12.3155",
    "florence": "43.7696,11.2558",
    "berlin": "52.5200,13.4050",
    "bonn": "50.7337,7.0982",
    "frankfurt": "50.1109,8.6821",
    "hamburg": "53.5511,9.9937",
    "munich": "48.1351,11.5820",
    "stuttgart": "48.7758,9.1829",
    "warsaw": "52.2297,21.0122",
    "krakow": "50.0647,19.9450",
    "moscow": "55.7558,37.6173",
    "saint petersburg": "59.9311,30.3609",
    "kiev": "50.4501,30.5234",
    "odessa": "46.4825,30.7233",
    "istanbul": "41.0082,28.9784",
    "jerusalem": "31.7683,35.2137",
    "tel aviv": "32.0853,34.7818",
    "cairo": "30.0444,31.2357",
    "riyadh": "24.7136,46.6753",
    "dubai": "25.2048,55.2708",
    "abu dhabi": "24.4539,54.3773",
    "sharjah": "25.3463,55.4209",
    "cape town": "-33.9249,18.4241",
    "johannesburg": "-26.2041,28.0473",
    "durban": "-29.8587,31.0218",
    "mumbai": "19.0760,72.8777",
    "pune": "18.5204,73.8567",
    "nashik": "19.9975,73.7898",
    "new delhi": "28.6139,77.2090",
    "amritsar": "31.6340,74.8723",
    "jaipur": "26.9124,75.7873",
    "udaipur": "24.5854,73.7125",
    "jodhpur": "26.2389,73.0243",
    "indore": "22.7196,75.8577",
    "bangalore": "12.9716,77.5946",
    "bengaluru": "12.9716,77.5946",
    "chennai": "13.0827,80.2707",
    "hyderabad": "17.3850,78.4867",
    "kochi": "9.9312,76.2673",
    "panjim": "15.4909,73.8278",
    "margao": "15.2832,73.9862",
    "vasco da gama": "15.3959,73.8143",
    "singapore": "1.3521,103.8198",
    "bangkok": "13.7563,100.5018",
    "ho chi minh city": "10.8231,106.6297",
    "manila": "14.5995,120.9842",
    "kuala lumper": "3.1390,101.6869",
    "jakarta": "-6.2088,106.8456",
    "shanghai": "31.2304,121.4737",
    "beijing": "39.9042,116.4074",
    "taipei": "25.0330,121.5654",
    "tokyo": "35.6762,139.6503",
    "osaka": "34.6937,135.5023",
    "seoul": "37.5665,126.9780",
    "perth": "-31.9505,115.8605",
    "adelaide": "-34.9285,138.6007",
    "melbourne": "-37.8136,144.9631",
    "sydney": "-33.8688,151.2093",
    "brisbane": "-27.4705,153.0260",
    "hobart": "-42.8821,147.3272",
    "christchurch": "-43.5321,172.6362",
    "wellington": "-41.2865,174.7762",
    "auckland": "-36.8485,174.7633",
}


async def web_search(query: str) -> str:
    """
    Performs a real-time web search to find the latest information.
    Use this for news, restaurant recommendations, or current events.
    This function uses Tavily search, so add TAVILY_API_KEY to your
    .env file to use it.

    NOTE: to be used as a web-search tool instead of google_search when using
    a non-Google LLM (such as OpenAI or Anthropic). ADK does not support using
    google tools (such as google_search) with a non-Google LLM, such as OpenAI

    Args:
        query: The search query string.
    """
    logger.info(f"🛠️ TOOL CALLED: web_search with query: '{query}'")

    api_key = os.environ.get("TAVILY_API_KEY")

    if not api_key:
        return "Error: TAVILY_API_KEY is not set in environment variables."

    # Tavily requires a specific JSON payload and Header
    url = "https://api.tavily.com/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": query[:400],  # Enforce the 400 char limit
        "search_depth": "basic",
        "max_results": 5,
    }

    async with httpx.AsyncClient() as client:
        try:
            # We use json=payload to ensure httpx serializes it correctly
            response = await client.post(
                url, headers=headers, json=payload, timeout=10.0
            )

            if response.status_code != 200:
                return f"Tavily API Error {response.status_code}: {response.text}"

            data = response.json()
            results = data.get("results", [])

            if not results:
                return "No search results found for this query."

            output = []
            for r in results:
                output.append(
                    f"Title: {r.get('title')}\nSource: {r.get('url')}\nContent: {r.get('content')}"
                )

            response = "\n\n---\n\n".join(output)
            logger.info(f"web_search(query='{query}') -> {response}")
            return response
        except Exception as e:
            logger.fatal(f"web_search(query='{query}') -> tool call failed: {e}")
            return f"An unexpected error occurred during search: {str(e)}"


def get_live_weather_global(location_name: str) -> dict:
    """
    Gets the current, real-time weather forecast for a specified location.
    NOTE: Only the cities in the LOCATION_COORDINATES dictionary are supported.
    You can expand this dictionary as needed.

    Args:
        location: The city name, e.g., "San Francisco".

    Returns:
        A dictionary containing the temperature and a detailed forecast.
        returned_json =  {
            "location": search_key,
            "status": "success",
            "temperature": "Temperature in °C",
            "feels_like": "Feels like temperature in °C",
            "humidity": "Relative humidity in %",
            "conditions": "Current weather conditions (e.g., "Clear", "Rainy")",
            "cloud_cover": "Cloud cover percentage",
            "pressure": "Current pressure in hPa",
            "precipitation": "Rainfall in mm",
            "wind_speed": "Wind speed in m/s",
        }
    """
    logger.info(f"🛠️ TOOL CALLED: get_live_weather_global(location='{location_name}')")

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
        response = {
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
        logger.info(
            f"get_live_weather_global(location='{location_name}') -> {response}"
        )
        return response
    except requests.exceptions.RequestException as e:
        logger.fatal(
            f"get_live_weather_global(location='{location_name}') -> API request failed: {e}"
        )
        return {"status": "error", "message": f"API request failed: {e}"}
