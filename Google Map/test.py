import requests 
from dotenv import load_dotenv 
import os  
import json
load_dotenv() 

url="https://maps.googleapis.com/maps/api/place/textsearch/json"
city="delhi"
query=f"find hotels in {city}"
API_KEY=os.getenv("GOOGLE_PLACES_API") 
params={
    "query":query,
    "key":API_KEY
}
response=requests.get(url,params=params)
data=response.json()
results = data.get("results", [])
print(results[0])