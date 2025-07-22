import os
import json

# Load farmer details from JSON
with open("Scheme_agent\\farmer_info.json", "r") as f:
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
from Scheme_agent.instructions import(
    SCHEME_EXPLAINER_INSTRUCTION,ELIGIBILITY_ANALYZER_INSTRUCTION,LINKS_INSTRUCTION,ORCHESTRATOR_INSTRUCTION 
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


orchestrator= SequentialAgent(
    name="Scheme_Analyzer",
    description=ORCHESTRATOR_INSTRUCTION,
    sub_agents=[scheme_explainer_agent,eligibility_analyzer_agent,link_finder_agent]
)

root_agent=orchestrator