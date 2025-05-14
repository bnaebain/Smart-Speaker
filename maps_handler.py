import requests
from config import GOOGLE_MAPS_API_KEY, GOOGLE_MAPS_HOME_ADDRESS
import time
import datetime
import pytz

KNOWN_LOCATIONS = {
    "work": "Stripe, 350 N Orleans St, Chicago, IL"
}

def get_place_address(query):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "key": GOOGLE_MAPS_API_KEY,
        "query": query,
    }

    response = requests.get(url, params=params)
    data = response.json()

    print("DEBUG: Places API query:", query)
    print("DEBUG: Places API response:", data)

    if data.get("results"):
        return data["results"][0]["formatted_address"]
    else:
        return None

def get_travel_time(destination, departure_time=None):
    dest_key = destination.lower().strip()

    # Step 1: Resolve the actual destination address
    if dest_key in KNOWN_LOCATIONS:
        resolved_place = KNOWN_LOCATIONS[dest_key]
        print(f"DEBUG: Using known location for '{dest_key}': {resolved_place}")
    else:
        query = f"{destination} near {GOOGLE_MAPS_HOME_ADDRESS}"
        resolved_place = get_place_address(query)
        print(f"DEBUG: Places API resolved '{destination}' to '{resolved_place}'")

    if not resolved_place:
        return f"Sorry, I couldn't find {destination} near home."

    # Step 2: Handle departure time
    tz = pytz.timezone("America/Chicago")  # Replace with your timezone
    now = datetime.datetime.now(tz)

    if departure_time:
        try:
            hour, minute = map(int, departure_time.split(":"))
            future_dt = tz.localize(datetime.datetime(now.year, now.month, now.day, hour, minute))

            if future_dt < now:
                future_dt += datetime.timedelta(days=1)

            timestamp = int(future_dt.timestamp())
            print(f"DEBUG: Departure timestamp = {timestamp} ({datetime.datetime.fromtimestamp(timestamp, tz)})")
        except Exception as e:
            print(f"⚠️ Time parsing error: {e}")
            timestamp = "now"
    else:
        timestamp = "now"

    # Step 3: Call Distance Matrix API
    params = {
        "origins": GOOGLE_MAPS_HOME_ADDRESS,
        "destinations": resolved_place,
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving",
        "units": "imperial",
        "departure_time": timestamp,
    }

    # Only include traffic_model if not 'now'
    if timestamp != "now":
        params["traffic_model"] = "best_guess"

    response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=params)
    data = response.json()
    print("DEBUG: Distance Matrix API raw response:", data)
    try:
        if data["status"] != "OK":
            return f"Google Maps error: {data['status']}"

        element = data["rows"][0]["elements"][0]
        if element["status"] != "OK":
            return f"Couldn’t get a route to {destination}: {element['status']}"

        distance = element["distance"]["text"]

        if departure_time and "duration_in_traffic" in element:
            duration = element["duration_in_traffic"]["text"]
        else:
            duration = element["duration"]["text"]

        if departure_time:
            return f"At {departure_time}, it’ll take about {duration} to get to {destination} — it’s {distance} from home."
        else:
            return f"It’ll take about {duration} to get to {destination} — it’s {distance} from home."
    except Exception as e:
        return f"Couldn’t get travel time. Error: {e}"