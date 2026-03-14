from google.adk.agents import Agent
from tools.mission_tools import generate_image
import os

asset_instruction = """
You are the ARC Asset Specialist. 
Your role is to generate visual assets for the mission, including explorer portraits, equipment schematics, and map icons.

## MULTI-TURN GENERATION
You have access to image generation capabilities. To maintain consistency (e.g., keeping the same explorer character), you should leverage the chat context. 

## YOUR TOOLS
- `generate_image`: Use this to create any visual asset requested.

When a user asks for an identity or a map icon, ensure you describe it vividly before calling the generation tool.
"""

asset_specialist = Agent(
    name="AssetSpecialist",
    model="gemini-2.5-flash",
    description="Specialist for generating mission-critical visual assets and identities.",
    instruction=asset_instruction,
    tools=[generate_image]
)
