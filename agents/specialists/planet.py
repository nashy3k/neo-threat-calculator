from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool
import os

# Placeholder for Data Store ID - User should update this
DATASTORE_ID = os.getenv("PLANET_DATASTORE_ID", "projects/YOUR_PROJECT/locations/global/collections/default_collection/dataStores/planet-data")

planet_search_tool = VertexAiSearchTool(
    data_store_id=DATASTORE_ID
)

planet_instruction = """
You are the Planet Specialist. You have access to a vast database of planetary data, biomes, and environmental conditions.
Use the VertexAiSearchTool to answer specific questions about the planet's geography, atmosphere, and local hazards.
Always cite your findings from the search results.
"""

planet_specialist = Agent(
    name="PlanetSpecialist",
    model="gemini-2.5-flash",
    description="Expert on planetary environment and data lookup.",
    instruction=planet_instruction,
    tools=[planet_search_tool]
)
