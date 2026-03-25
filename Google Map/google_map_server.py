from fastmcp import FastMCP 
import requests
from dotenv import load_dotenv
import os  

load_dotenv()

mcp=FastMCP("google_places")
API_KEY=os.getenv("GOOGLE_PLACES_API") 

@mcp.tool()
def search_hotels(city:str,max_price:int = 5000):

    if not API_KEY:
        return {"error": "API key missing"}
    
    url="https://maps.googleapis.com/maps/api/place/textsearch/json"

    query=f"find hotels in {city}"
    
    params={
        "query":query,
        "key":API_KEY
    }
    response=requests.get(url,params=params)
    data=response.json()
    results = data.get("results", [])
    hotels = []

    for place in results:
        name = place.get("name")
        rating = place.get("rating", 0)
        address = place.get("formatted_address")

        # Google gives price_level (0–4)
        price_level = place.get("price_level", 2)

        # Convert to rough INR estimate
        estimated_price = (price_level + 1) * 1000

        if estimated_price <= max_price:
            hotels.append({
                "name": name,
                "rating": rating,
                "price_estimate": estimated_price,
                "address": address
            })

    # Sort by rating
    hotels.sort(key=lambda x: x["rating"], reverse=True)
    return hotels[:5]

if __name__ == "__main__":
    mcp.run()


