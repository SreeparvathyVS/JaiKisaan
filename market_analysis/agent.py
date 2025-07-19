# agent.py

import os
from dotenv import load_dotenv
import requests
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent,Agent
from google.adk.tools import google_search
import datetime

OPENWEATHER_API_KEY = "b87e5591eba704412e06ce4976c90ee3"

from market_analysis.instructions import (
    MARKET_ANALYSIS_COORDINATOR_INSTRUCTION,
    PRICE_DATA_FETCHER_INSTRUCTION,
    MARKET_TREND_ANALYZER_INSTRUCTION,
    WEATHER_AGENT_INSTRUCTION,
    MARKET_RECOMMENDATION_AGENT_INSTRUCTION,
    FINAL_RESPONSE_SYNTHESIZER_INSTRUCTION
)

# Load env variables
load_dotenv()
MODEL_NAME = os.environ.get("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
def weather_advisory_tool(state: dict) -> dict:
    """
    Fetch 7-day weather forecast from OpenWeatherMap based on crop location.
    """
    location = state.get("location")
    if not location:
        return {"error": "Location not provided in state."}
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={OPENWEATHER_API_KEY}"
    geo_res = requests.get(geocode_url).json()
    if not geo_res:
        return {"error": "Invalid location"}

    lat = geo_res[0]["lat"]
    lon = geo_res[0]["lon"]

    weather_url = (
        f"https://api.openweathermap.org/data/2.5/onecall"
        f"?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&units=metric&appid={OPENWEATHER_API_KEY}"
    )
    weather_res = requests.get(weather_url).json()

    forecast = []
    for daily in weather_res.get("daily", []):
        date = datetime.datetime.fromtimestamp(daily["dt"]).strftime("%Y-%m-%d")
        forecast.append({
            "date": date,
            "temp_min": daily["temp"]["min"],
            "temp_max": daily["temp"]["max"],
            "humidity": daily["humidity"],
            "rain": daily.get("rain", 0),
            "weather": daily["weather"][0]["description"]
        })

    state['weather_advisory'] = {
        "forecast": forecast
    }
    return state


# === Intent + Crop + Location Extractor (initial coordinator) ===
intent_extractor_agent = LlmAgent(
    name="IntentExtractor",
    model=MODEL_NAME,
    instruction=MARKET_ANALYSIS_COORDINATOR_INSTRUCTION,
    output_key="parsed_intent"  # Will include crop, location, and user intent
)

# === Farmer DB Agent (mocked/fake DB call, could be another LLM or API call) ===
# If it's not an LLM, this will be a tool or custom function in real setup.

# === Price Fetcher ===
#price_data=fetch_price_data(crop, location)
price_data_fetcher_agent=LlmAgent(
    name="PRICE_DATA_FETCHER_INSTRUCTION",
    model=MODEL_NAME,
    instruction=PRICE_DATA_FETCHER_INSTRUCTION,
    tools=[google_search],
    output_key="price_data"  # Will include crop, location, and user intent
)
weather_agent=LlmAgent(
    name="weather_agent",
    tools=[weather_advisory_tool],
    model=MODEL_NAME,
    instruction=WEATHER_AGENT_INSTRUCTION,
    output_key="weather_advisory"
)
# === Weather Agent ===


# === Calendar/Festival Agent ===

# === Trend Analyzer (runs after price) ===
trend_analyzer_agent = LlmAgent(
    name="TrendAnalyzer",
    model=MODEL_NAME,
    instruction=MARKET_TREND_ANALYZER_INSTRUCTION,
    output_key="trend_analysis"
)

# === Recommendation Agent ===
recommendation_agent = LlmAgent(
    name="RecommendationAgent",
    model=MODEL_NAME,
    instruction=MARKET_RECOMMENDATION_AGENT_INSTRUCTION,
    output_key="recommendation"
)

# === Final Synthesizer ===
final_response_agent = LlmAgent(
    name="FinalResponseSynthesizer",
    model=MODEL_NAME,
    instruction=FINAL_RESPONSE_SYNTHESIZER_INSTRUCTION
)

# === Parallel Sub-Agent Group (Weather, Calendar) ===
weatherandpriceagent=ParallelAgent(
    name="priceagents",
    sub_agents=[weather_agent,price_data_fetcher_agent]
)


# === Full Sequential Chain ===
market_analysis_flow = SequentialAgent(
    name="MarketAnalysisCoordinator",
    sub_agents=[
        intent_extractor_agent,
        weatherandpriceagent,
        trend_analyzer_agent,  
        recommendation_agent,
        final_response_agent
    ]
)

# Exposed root agent to ADK runtime
root_agent = market_analysis_flow
