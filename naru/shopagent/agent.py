import requests


import requests

def find_nearby_shops(location: str, radius: int = 1000, shop_type: str = "store") -> list:
    """
    Uses Google Maps Places API to find nearby shops.
    
    Args:
        location (str): A string like "12.9716,77.5946" (latitude,longitude).
        radius (int): Search radius in meters.
        shop_type (str): Type of shop to search for (e.g., 'store', 'supermarket', 'pharmacy').

    Returns:
        list: A list of dictionaries with shop names and addresses.
    """
   
    url = "http://wiki.openstreetmap.org/wiki/API"
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "location": location,
        "radius": radius,
        "type": shop_type,
        "key": api_key
    }

    response = requests.get(url, params=params)
    results = response.json().get("results", [])

    shops = []
    for place in results:
        shops.append({
            "name": place.get("name"),
            "address": place.get("vicinity")
        })

    return shops
#
import os
import json

# Load farmer details from JSON
with open("marketagent\\farmer_info.json", "r") as f:
    farmer_info = json.load(f)

try:
    from dotenv import load_dotenv
    load_dotenv()

    MODEL_NAME = os.environ.get("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
except ImportError:
    print("Warning: python-dotenv not installed. Ensure API key is set")
    MODEL_NAME = "gemini-2.0-flash"

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from shopagent.instructions import(SHOP_FINDER_INSTRUCTION, ORCHESTRATOR_INSTRUCTION)

shop_finder_agent = LlmAgent(
    name="Shop_Finder",
    model=MODEL_NAME,
    instruction=SHOP_FINDER_INSTRUCTION,
    tools=[find_nearby_shops],
    output_key="shops_found"
)
orchestrator= SequentialAgent(
    name="Shop_Finder_Orchestrator",
    description=ORCHESTRATOR_INSTRUCTION,
    sub_agents=[shop_finder_agent]
)

root_agent=orchestrator