import datetime
from zoneinfo import ZoneInfo

import os
import requests

LOCATION_COORDINATES_AND_TZ = {
    "honolulu": ("21.3069,-157.8583", "Pacific/Honolulu"),
    "anchorage": ("61.2181,-149.9003", "America/Anchorage"),
    "seattle": ("47.6062,-122.3321", "America/Los_Angeles"),
    "redmond": ("47.6740,-122.1215", "America/Los_Angeles"),
    "portland": ("45.5152,-122.6784", "America/Los_Angeles"),
    "sunnyvale": ("37.3688,-122.0363", "America/Los_Angeles"),
    "san francisco": ("37.7749,-122.4194", "America/Los_Angeles"),
    "san jose": ("37.3382,-121.8863", "America/Los_Angeles"),
    "lake tahoe": ("39.0968,-120.0324", "America/Los_Angeles"),
    "los angeles": ("34.0522,-118.2437", "America/Los_Angeles"),
    "san diego": ("32.7157,-117.1611", "America/Los_Angeles"),
    "las vegas": ("36.1699,-115.1398", "America/Los_Angeles"),
    "phoenix": ("33.4484,-112.0740", "America/Phoenix"),
    "tucson": ("32.2226,-110.9747", "America/Phoenix"),
    "salt lake city": ("40.7608,-111.8910", "America/Denver"),
    "denver": ("39.7392,-104.9903", "America/Denver"),
    "albuquerque": ("35.0844,-106.6504", "America/Denver"),
    "houston": ("29.7604,-95.3698", "America/Chicago"),
    "dallas": ("32.7767,-96.7970", "America/Chicago"),
    "san antonio": ("29.4241,-98.4936", "America/Chicago"),
    "austin": ("30.2672,-97.7431", "America/Chicago"),
    "new orleans": ("29.9511,-90.0715", "America/Chicago"),
    "memphis": ("35.1495,-90.0490", "America/Chicago"),
    "nashville": ("36.1627,-86.7816", "America/Chicago"),
    "atlanta": ("33.7490,-84.3880", "America/New_York"),
    "augusta": ("33.4735,-82.0105", "America/New_York"),
    "savannah": ("32.0809,-81.0912", "America/New_York"),
    "tampa": ("27.9506,-82.4572", "America/New_York"),
    "miami": ("25.7617,-80.1918", "America/New_York"),
    "orlando": ("28.5383,-81.3792", "America/New_York"),
    "charlotte": ("35.2271,-80.8431", "America/New_York"),
    "st louis": ("38.6270,-90.1994", "America/Chicago"),
    "louisville": ("38.2527,-85.7585", "America/Kentucky/Louisville"),
    "indianapolis": ("39.7684,-86.1581", "America/Indiana/Indianapolis"),
    "chicago": ("41.8781,-87.6298", "America/Chicago"),
    "milwaukee": ("43.0389,-87.9065", "America/Chicago"),
    "minneapolis": ("44.9778,-93.2650", "America/Chicago"),
    "detroit": ("42.3314,-83.0458", "America/Detroit"),
    "cleveland": ("41.4993,-81.6944", "America/New_York"),
    "cincinnati": ("39.1031,-84.5120", "America/New_York"),
    "columbus": ("39.9612,-82.9988", "America/New_York"),
    "washington, dc": ("38.9072,-77.0369", "America/New_York"),
    "baltimore": ("39.2904,-76.6122", "America/New_York"),
    "pittsburgh": ("40.4406,-79.9959", "America/New_York"),
    "philadelphia": ("39.9526,-75.1652", "America/New_York"),
    "allentown": ("40.6023,-75.4714", "America/New_York"),
    "hershey": ("40.2859,-76.6502", "America/New_York"),
    "richmond": ("37.5407,-77.4360", "America/New_York"),
    "new york": ("40.7128,-74.0060", "America/New_York"),
    "newark": ("40.7357,-74.1724", "America/New_York"),
    "new haven": ("41.3083,-72.9279", "America/New_York"),
    "newport": ("41.4901,-71.3128", "America/New_York"),
    "providence": ("41.8240,-71.4128", "America/New_York"),
    "boston": ("42.3601,-71.0589", "America/New_York"),
    "worcester": ("42.2626,-71.8023", "America/New_York"),
    "toronto": ("43.6532,-79.3832", "America/Toronto"),
    "montreal": ("45.5017,-73.5673", "America/Toronto"),
    "ottawa": ("45.4215,-75.6972", "America/Toronto"),
    "vancouver": ("49.2827,-123.1207", "America/Vancouver"),
    "quebec city": ("46.8139,-71.2080", "America/Toronto"),
    "winnipeg": ("49.8951,-97.1384", "America/Winnipeg"),
    "calgary": ("51.0447,-114.0719", "America/Edmonton"),
    "edmonton": ("53.5461,-113.4938", "America/Edmonton"),
    "london": ("51.5074,-0.1278", "Europe/London"),
    "liverpool": ("53.4084,-2.9916", "Europe/London"),
    "manchester": ("53.4808,-2.2426", "Europe/London"),
    "birmingham": ("52.4862,-1.8904", "Europe/London"),
    "oxford": ("51.7520,-1.2577", "Europe/London"),
    "cambridge": ("52.2053,0.1218", "Europe/London"),
    "leeds": ("53.8008,-1.5491", "Europe/London"),
    "edinburgh": ("55.9533,-3.1883", "Europe/London"),
    "glasgow": ("55.8642,-4.2518", "Europe/London"),
    "belfast": ("54.5973,-5.9301", "Europe/London"),
    "dublin": ("53.3498,-6.2603", "Europe/Dublin"),
    "amsterdam": ("52.3676,4.9041", "Europe/Amsterdam"),
    "rotterdam": ("51.9225,4.4792", "Europe/Amsterdam"),
    "brussels": ("50.8503,4.3517", "Europe/Brussels"),
    "antwerp": ("51.2194,4.4025", "Europe/Brussels"),
    "paris": ("48.8566,2.3522", "Europe/Paris"),
    "marseille": ("43.2965,5.3698", "Europe/Paris"),
    "bordeaux": ("44.8378,-0.5792", "Europe/Paris"),
    "madrid": ("40.4168,-3.7038", "Europe/Madrid"),
    "barcelona": ("41.3851,2.1734", "Europe/Madrid"),
    "lisbon": ("38.7223,-9.1393", "Europe/Lisbon"),
    "porto": ("41.1579,-8.6291", "Europe/Lisbon"),
    "zurich": ("47.3769,8.5417", "Europe/Zurich"),
    "basel": ("47.5596,7.5886", "Europe/Zurich"),
    "geneva": ("46.2044,6.1432", "Europe/Zurich"),
    "rome": ("41.9028,12.4964", "Europe/Rome"),
    "milan": ("45.4642,9.1900", "Europe/Rome"),
    "venice": ("45.4408,12.3155", "Europe/Rome"),
    "florence": ("43.7696,11.2558", "Europe/Rome"),
    "berlin": ("52.5200,13.4050", "Europe/Berlin"),
    "bonn": ("50.7337,7.0982", "Europe/Berlin"),
    "frankfurt": ("50.1109,8.6821", "Europe/Berlin"),
    "hamburg": ("53.5511,9.9937", "Europe/Berlin"),
    "munich": ("48.1351,11.5820", "Europe/Berlin"),
    "stuttgart": ("48.7758,9.1829", "Europe/Berlin"),
    "warsaw": ("52.2297,21.0122", "Europe/Warsaw"),
    "krakow": ("50.0647,19.9450", "Europe/Warsaw"),
    "moscow": ("55.7558,37.6173", "Europe/Moscow"),
    "saint petersburg": ("59.9311,30.3609", "Europe/Moscow"),
    "kiev": ("50.4501,30.5234", "Europe/Kyiv"),
    "odessa": ("46.4825,30.7233", "Europe/Kyiv"),
    "istanbul": ("41.0082,28.9784", "Europe/Istanbul"),
    "jerusalem": ("31.7683,35.2137", "Asia/Jerusalem"),
    "tel aviv": ("32.0853,34.7818", "Asia/Jerusalem"),
    "cairo": ("30.0444,31.2357", "Africa/Cairo"),
    "riyadh": ("24.7136,46.6753", "Asia/Riyadh"),
    "dubai": ("25.2048,55.2708", "Asia/Dubai"),
    "abu dhabi": ("24.4539,54.3773", "Asia/Dubai"),
    "sharjah": ("25.3463,55.4209", "Asia/Dubai"),
    "cape town": ("-33.9249,18.4241", "Africa/Johannesburg"),
    "johannesburg": ("-26.2041,28.0473", "Africa/Johannesburg"),
    "durban": ("-29.8587,31.0218", "Africa/Johannesburg"),
    "mumbai": ("19.0760,72.8777", "Asia/Kolkata"),
    "pune": ("18.5204,73.8567", "Asia/Kolkata"),
    "nashik": ("19.9975,73.7898", "Asia/Kolkata"),
    "kolhapur": ("16.7050,74.2433", "Asia/Kolkata"),
    "solapur": ("17.6599,75.9064", "Asia/Kolkata"),
    "sangli": ("16.8524,74.5815", "Asia/Kolkata"),
    "mahabaleshwar": ("17.9307,73.6477", "Asia/Kolkata"),
    "lonavala": ("18.7541,73.4063", "Asia/Kolkata"),
    "shirdi": ("19.7663,74.4754", "Asia/Kolkata"),
    "ahmednagar": ("19.0952,74.7496", "Asia/Kolkata"),
    "sambhajinagar": ("19.8762,75.3433", "Asia/Kolkata"),  # Formerly Aurangabad
    "new delhi": ("28.6139,77.2090", "Asia/Kolkata"),
    "amritsar": ("31.6340,74.8723", "Asia/Kolkata"),
    "jaipur": ("26.9124,75.7873", "Asia/Kolkata"),
    "udaipur": ("24.5854,73.7125", "Asia/Kolkata"),
    "jodhpur": ("26.2389,73.0243", "Asia/Kolkata"),
    "indore": ("22.7196,75.8577", "Asia/Kolkata"),
    "bangalore": ("12.9716,77.5946", "Asia/Kolkata"),
    "bengaluru": ("12.9716,77.5946", "Asia/Kolkata"),
    "chennai": ("13.0827,80.2707", "Asia/Kolkata"),
    "hyderabad": ("17.3850,78.4867", "Asia/Kolkata"),
    "kochi": ("9.9312,76.2673", "Asia/Kolkata"),
    "panjim": ("15.4909,73.8278", "Asia/Kolkata"),
    "margao": ("15.2832,73.9862", "Asia/Kolkata"),
    "vasco da gama": ("15.3959,73.8143", "Asia/Kolkata"),
    "mapusa": ("15.5937,73.8142", "Asia/Kolkata"),
    "thivim": ("15.6219,73.8447", "Asia/Kolkata"),
    "karmali": ("15.4851,73.9189", "Asia/Kolkata"),
    "chandigarh": ("30.7333,76.7794", "Asia/Kolkata"),
    "shimla": ("31.1048,77.1734", "Asia/Kolkata"),
    "jalandhar": ("31.3260,75.5762", "Asia/Kolkata"),
    "ludhiana": ("30.9010,75.8573", "Asia/Kolkata"),
    "srinagar": ("34.0837,74.7973", "Asia/Kolkata"),
    "lucknow": ("26.8467,80.9462", "Asia/Kolkata"),
    "kanpur": ("26.4499,80.3319", "Asia/Kolkata"),
    "noida": ("28.5355,77.3910", "Asia/Kolkata"),
    "patna": ("25.5941,85.1376", "Asia/Kolkata"),
    "kolkata": ("22.5726,88.3639", "Asia/Kolkata"),
    "bhuvaneshwar": ("20.2961,85.8245", "Asia/Kolkata"),
    "hyderabad": ("17.3850,78.4867", "Asia/Kolkata"),
    "vishakapatnam": ("17.6868,83.2185", "Asia/Kolkata"),
    "puducherry": ("11.9416,79.8083", "Asia/Kolkata"),
    "thirvananthapuram": ("8.5241,76.9366", "Asia/Kolkata"),
    "mysore": ("12.2958,76.6394", "Asia/Kolkata"),
    "mangalore": ("12.9141,74.8560", "Asia/Kolkata"),
    "mangaluru": ("12.9141,74.8560", "Asia/Kolkata"),
    "udupi": ("13.3409,74.7421", "Asia/Kolkata"),
    "ahmedabad": ("23.0225,72.5714", "Asia/Kolkata"),
    "surat": ("21.1702,72.8311", "Asia/Kolkata"),
    "gandhinagar": ("23.2156,72.6369", "Asia/Kolkata"),
    "ujjain": ("23.1760,75.7885", "Asia/Kolkata"),
    "bhopal": ("23.2599,77.4126", "Asia/Kolkata"),
    "singapore": ("1.3521,103.8198", "Asia/Singapore"),
    "bangkok": ("13.7563,100.5018", "Asia/Bangkok"),
    "ho chi minh city": ("10.8231,106.6297", "Asia/Ho_Chi_Minh"),
    "manila": ("14.5995,120.9842", "Asia/Manila"),
    "kuala lumper": ("3.1390,101.6869", "Asia/Kuala_Lumpur"),
    "jakarta": ("-6.2088,106.8456", "Asia/Jakarta"),
    "shanghai": ("31.2304,121.4737", "Asia/Shanghai"),
    "beijing": ("39.9042,116.4074", "Asia/Shanghai"),
    "taipei": ("25.0330,121.5654", "Asia/Taipei"),
    "tokyo": ("35.6762,139.6503", "Asia/Tokyo"),
    "osaka": ("34.6937,135.5023", "Asia/Tokyo"),
    "seoul": ("37.5665,126.9780", "Asia/Seoul"),
    "perth": ("-31.9505,115.8605", "Australia/Perth"),
    "adelaide": ("-34.9285,138.6007", "Australia/Adelaide"),
    "melbourne": ("-37.8136,144.9631", "Australia/Melbourne"),
    "sydney": ("-33.8688,151.2093", "Australia/Sydney"),
    "brisbane": ("-27.4705,153.0260", "Australia/Brisbane"),
    "hobart": ("-42.8821,147.3272", "Australia/Hobart"),
    "christchurch": ("-43.5321,172.6362", "Pacific/Auckland"),
    "wellington": ("-41.2865,174.7762", "Pacific/Auckland"),
    "auckland": ("-36.8485,174.7633", "Pacific/Auckland"),
}


def get_weather(city: str) -> str:
    """Retrieves the current weather report for a specified city.
    Args:
        city: The name of the city for which to retrieve the weather report.
    Returns:
        A dict with 'status' and either 'report' or 'error_message'.
    """

    print(f"🛠️ TOOL CALLED: get_weather(city='{city}')")

    # we will use the free open-meteo API to fetch weather info
    # 1. Normalize and Lookup Coordinates
    search_key = city.lower().strip()
    coords_and_tz_str = LOCATION_COORDINATES_AND_TZ.get(search_key)
    print(f"   - get_weather(city='{city}') -> coords_and_tz_str: {coords_and_tz_str}")

    if not coords_and_tz_str:
        return {
            "status": "error",
            "message": f"Coordinates for '{city}' not found.",
        }

    # 2. Parse string "lat,lon" into floats
    try:
        lat, lon = map(float, coords_and_tz_str[0].split(","))
        print(f"   - get_weather(city='{city}') -> lat: {lat}, lon: {lon}")
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
        # and ask for these details
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
        "timezone": "auto",
    }

    try:
        print(f"   - get_weather(city='{city}') -> API request: {url}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        ret = {
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
        print(f"   - get_weather(city='{city}') -> got response: {ret}")
        return ret
    except requests.exceptions.RequestException as e:
        print(f"   - get_weather(city='{city}') -> API request failed: {e}")
        return {"status": "error", "message": f"API request failed: {e}"}


# def get_weather(city: str) -> dict:
#     """Retrieves the current weather report for a specified city.

#     Args:
#         city: The name of the city for which to retrieve the weather report.

#     Returns:
#         A dict with 'status' and either metrics or 'message'.
#     """
#     print(f"🛠️ TOOL CALLED: get_weather(city='{city}')")

#     # 1. Fetch API Key from the Environment
#     api_key = os.getenv("WEATHERAPI_KEY")
#     if not api_key:
#         return {
#             "status": "error",
#             "message": "Environment variable 'WEATHERAPI_KEY' is missing.",
#         }

#     # 2. Normalize input string
#     search_key = city.lower().strip()

#     # 3. Call WeatherAPI.com (Current endpoint)
#     # Note: WeatherAPI accepts the city name string directly for the 'q' parameter!
#     url = "http://api.weatherapi.com/v1/current.json"
#     params = {
#         "key": api_key,
#         "q": search_key,  # Natively handles names like 'mumbai', 'london', etc.
#         "aqi": "no",
#     }

#     try:
#         print(f"   - get_weather(city='{city}') -> API request: {url}")
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()

#         current = data["current"]
#         print(f"   - get_weather(city='{city}') -> got response data successfully.")

#         # 4. Map parameters to match your original schema format exactly
#         return {
#             "location": data["location"]["name"].lower(),
#             "status": "success",
#             "temperature": f"{current['temp_c']}°C",
#             "feels_like": f"{current['feelslike_c']}°C",
#             "humidity": f"{current['humidity']}%",
#             "conditions": current["condition"][
#                 "text"
#             ],  # Human readable text instead of a numeric code!
#             "cloud_cover": f"{current['cloud']}%",
#             "pressure": f"{current['pressure_mb']} hPa",
#             "precipitation": f"{current['precip_mm']} mm",
#             "wind_speed": f"{current['wind_kph']} kph",  # WeatherAPI returns wind in kph
#         }

#     except requests.exceptions.RequestException as e:
#         print(f"   - get_weather(city='{city}') -> API request failed: {e}")
#         return {"status": "error", "message": f"API request failed: {e}"}


# -------------------------------------------------------------
# Simple tooks. limited to NYC for demo purposes. No API calls
# -------------------------------------------------------------


# def get_weather(city: str) -> dict:
#     """Retrieves the current weather report for a specified city.
#     Args:
#         city: The name of the city for which to retrieve the weather report.
#     Returns:
#         A dict with 'status' and either 'report' or 'error_message'.
#     """
#     # In a real application you'd call a weather API here - e.g. OpenWeatherMap.
#     # We're keeping it hardcoded so nothing can go wrong on your first run.
#     if city.lower() == "new york":
#         return {
#             "status": "success",
#             "report": "Sunny, 25°C (77°F). Perfect weather for a walk.",
#         }
#     return {
#         "status": "error",
#         "error_message": f"No weather data available for '{city}'.",
#     }


def get_current_time(city: str) -> dict:
    """Returns the current local time in a specified city.
    Args:
        city: The name of the city for which to retrieve the current time.
    Returns:
        A dict with 'status' and either 'current time' or 'error_message'.
    """

    print(f"🛠️ TOOL CALLED: get_current_time(city='{city}')")

    # we will use the free open-meteo API to fetch weather info
    # 1. Normalize and Lookup Coordinates
    search_key = city.lower().strip()
    coords_and_tz_str = LOCATION_COORDINATES_AND_TZ.get(search_key)
    print(
        f"   - get_current_time(city='{city}') -> coords_and_tz_str: {coords_and_tz_str}"
    )

    if not coords_and_tz_str:
        return {
            "status": "error",
            "message": f"IANA timezone for '{city}' not found.",
        }

    tzs = coords_and_tz_str[1].strip()
    print(f"   - get_current_time(city='{city}') -> tz: {tzs}")

    tz = ZoneInfo(tzs)  # standard IANA timezone ID
    now = datetime.datetime.now(tz)
    return {
        "status": "success",
        "report": f"Current time in New York: {now.strftime('%H:%M:%S %Z')}",
    }

    # if city.lower() == "new york":
    #     tz = ZoneInfo("America/New_York")  # standard IANA timezone ID
    #     now = datetime.datetime.now(tz)
    #     return {
    #         "status": "success",
    #         "report": f"Current time in New York: {now.strftime('%H:%M:%S %Z')}",
    #     }
    # return {
    #     "status": "error",
    #     "error_message": f"No timezone information available for '{city}'.",
    # }
