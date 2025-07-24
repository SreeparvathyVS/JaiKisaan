import os
import json


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

#main code starts
try:
    from dotenv import load_dotenv
    load_dotenv()

    MODEL_NAME = os.environ.get("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
except ImportError:
    print("Warning: python-dotenv not installed. Ensure API key is set")
    MODEL_NAME = "gemini-2.0-flash"

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from Scheme_agent.instructions import(
    SCHEME_EXPLAINER_INSTRUCTION,ELIGIBILITY_ANALYZER_INSTRUCTION,LINKS_INSTRUCTION,FARMERPROFILE_RESOLVER_AGENT_INSTRUCTION,ORCHESTRATOR_INSTRUCTION 
)

scheme_explainer_agent = LlmAgent(
    name="Scheme_Explainer",
    model=MODEL_NAME,
    instruction=SCHEME_EXPLAINER_INSTRUCTION,
    tools=[google_search],
    output_key="scheme_summary"
)
# --- Sub Agent 2: MessagingStrategist ---
eligibility_analyzer_agent = LlmAgent(
    name="Eligibility_Analyzer",
    model=MODEL_NAME,  # Using environment variable
    instruction=ELIGIBILITY_ANALYZER_INSTRUCTION,
    # This agent will automatically receive the output of the previous agent (scheme analyzer)
    # and can also access other state variables if needed, e.g.,
    output_key="eligibility" # Save result to state under this key
)


# --- Sub Agent 3:Linkfinder ---
link_finder_agent = LlmAgent(
    name="LinkFinder",
    model=MODEL_NAME,  # Using environment variable
    instruction=LINKS_INSTRUCTION,
     tools=[google_search],
    output_key="links" # Save result to state
)

#===Location Resolver====
FarmerProfile_resolver_agent=LlmAgent(
    name="FarmerProfile_resolver_agent",
    model=MODEL_NAME,
    tools=[extract_information_into_state],
    instruction=FARMERPROFILE_RESOLVER_AGENT_INSTRUCTION
    
)
# --- Sub Agent 5: Output Consolidator ---
output_consolidator_agent = LlmAgent(
    name="Output_Consolidator",
    model=MODEL_NAME,
    instruction= """
You are a JSON Consolidator Agent. Your job is to take all the outputs from previous agents — such as scheme_summary, eligibility, and links — and compile them into a single well-structured JSON object. Ensure the structure is clean, key names are clear, and the content is nested logically where appropriate.
""",
    output_key="final_json"
)

orchestrator= SequentialAgent(
    name="Scheme_Analyzer",
    description=ORCHESTRATOR_INSTRUCTION,
    sub_agents=[FarmerProfile_resolver_agent,scheme_explainer_agent,eligibility_analyzer_agent,link_finder_agent,output_consolidator_agent]
)

root_agent=orchestrator