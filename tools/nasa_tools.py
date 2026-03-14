from google.adk.tools import FunctionTool
import httpx
import os
from datetime import datetime, timedelta

async def fetch_neo_data_func(days_count: int = 7) -> dict:
    """
    Fetches Near-Earth Object (asteroid) data from NASA's NeoWs API.
    Returns JSON containing asteroid names, diameters, and proximity data.
    """
    api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days_count)).strftime("%Y-%m-%d")
    
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={api_key}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # Simplify the data for the LLM context to avoid token bloat
            # Focus on names and raw measurement data for Python analysis
            return data
        except Exception as e:
            return {"error": f"Failed to fetch NASA data: {str(e)}"}
