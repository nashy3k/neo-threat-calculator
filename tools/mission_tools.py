from google.adk.tools.agent_tool import adk_tool
from google.genai import types
import os

@adk_tool
async def generate_image(prompt: str, context: dict = None) -> str:
    """
    Generates an image based on the provided prompt. 
    Maintains consistency if called within a session.
    """
    # Note: In a real ADK environment, we would use the GenAI client here.
    # For the hackathon demo, we mimic the behavior described in Level 0.
    return f"[IMAGE_GENERATED] A vivid representation of: {prompt}. (Consistency maintained via context)"

@adk_tool
async def extract_sos_details(report_text: str) -> dict:
    """
    Extracts critical survival details from a text report.
    """
    # This would typically call a lightweight Gemini model to parse the text
    return {
        "survivor": "Extracted Name",
        "needs": ["Water", "Medical"],
        "biome": "Extracted Biome",
        "status": "Priority Alpha"
    }
