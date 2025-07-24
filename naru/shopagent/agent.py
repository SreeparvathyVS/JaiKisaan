import requests


import requests

import os
import json

# Load farmer details from JSON
#with open("marketagent\\farmer_info.json", "r") as f:
 #   farmer_info = json.load(f)

def extract_information_into_state(state: dict) -> dict:
    """
    Extracts full farmer profile from a hardcoded farmer_info.json file and updates the state in the format:
    state['info'] = { full farmer profile }

    Args:
        state (dict): Optional state dictionary to update.

    Returns:
        dict: Updated state with full farmer profile under 'info'.
    """
    with open("farmer_info.json", "r") as f:
        farmer_json = json.load(f)

    state["info"] = farmer_json
    return state

try:
    from dotenv import load_dotenv
    load_dotenv()

    MODEL_NAME = os.environ.get("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
except ImportError:
    print("Warning: python-dotenv not installed. Ensure API key is set")
    MODEL_NAME = "gemini-2.5-flash"

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from shopagent.instructions import(FARMERPROFILE_RESOLVER_AGENT_INSTRUCTION,SHOP_FINDER_INSTRUCTION, ORCHESTRATOR_INSTRUCTION)

shop_finder_agent = LlmAgent(
    name="Shop_Finder",
    model=MODEL_NAME,
    instruction=SHOP_FINDER_INSTRUCTION,
    tools=[google_search],
    output_key="shops_found"
)
#===Location Resolver====
FarmerProfile_resolver_agent=LlmAgent(
    name="FarmerProfile_resolver_agent",
    model=MODEL_NAME,
    tools=[extract_information_into_state],
    instruction=FARMERPROFILE_RESOLVER_AGENT_INSTRUCTION
    
)
orchestrator= SequentialAgent(
    name="Shop_Finder_Orchestrator",
    description=ORCHESTRATOR_INSTRUCTION,
    sub_agents=[FarmerProfile_resolver_agent,shop_finder_agent]
)

root_agent=orchestrator