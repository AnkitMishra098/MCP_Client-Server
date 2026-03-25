from fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Flight Server")
API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

def get_IATA(city):
    if not city:
        return None
    CITY_TO_IATA = {
    "delhi": "DEL",
    "mumbai": "BOM",
    "bangalore": "BLR",
    "new york": "JFK",
    "london": "LHR"
}
    return CITY_TO_IATA.get(city.lower(), city)

@mcp.tool()
def search_flight(departure: str, arrival: str = None, date: str = None):
    departure=get_IATA(departure)
    arrival=get_IATA(arrival)
    if not API_KEY:
        return {"error": "API key missing"}

    url = "http://api.aviationstack.com/v1/flights"
    
    # Only allowed param in free plan
    params = {
        "access_key": API_KEY,
        "dep_iata": departure
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {"error": "API failed", "status": response.status_code}

    data = response.json()
    flights = data.get("data", [])

    # 🔥 Manual filtering (VERY IMPORTANT)
    filtered = []

    for flight in flights:
        dep = flight.get("departure", {}).get("iata")
        arr = flight.get("arrival", {}).get("iata")
        f_date = flight.get("flight_date")

        # Apply filters safely
        if arrival and arr != arrival:
            continue
        # if date and f_date != date:
        #     continue

        filtered.append({
            "flight": flight.get("flight", {}).get("iata"),
            "airline": flight.get("airline", {}).get("name"),
            "departure_airport": flight.get("departure", {}).get("airport"),
            "arrival_airport": flight.get("arrival", {}).get("airport"),
            "departure_time": flight.get("departure", {}).get("scheduled"),
            "arrival_time": flight.get("arrival", {}).get("scheduled"),
            "status": flight.get("flight_status"),
            "date": f_date
        })

    # Limit output
    return filtered[:5]


if __name__ == "__main__":
    mcp.run()