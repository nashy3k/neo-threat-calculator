from google.adk.tools import FunctionTool
import httpx
import os
from datetime import datetime, timedelta
from config.secrets import get_secret

async def fetch_neo_data_func(days_count: int = 7) -> dict:
    """
    Fetches Near-Earth Object (asteroid) data from NASA's NeoWs API.
    Returns JSON containing asteroid names, diameters, and proximity data.
    """
    api_key = get_secret("NASA_API_KEY")
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days_count)).strftime("%Y-%m-%d")
    
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={api_key}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # Summarize the data to reduce payload size and context bloat
            # Extract only essential fields for analysis
            simplified_data = {"near_earth_objects": {}}
            for date, objects in data.get("near_earth_objects", {}).items():
                simplified_data["near_earth_objects"][date] = []
                for obj in objects:
                    simplified_data["near_earth_objects"][date].append({
                        "name": obj.get("name"),
                        "id": obj.get("id"),
                        "estimated_diameter": obj.get("estimated_diameter"),
                        "is_potentially_hazardous_asteroid": obj.get("is_potentially_hazardous_asteroid"),
                        "close_approach_data": [{
                            "relative_velocity": obj["close_approach_data"][0]["relative_velocity"],
                            "miss_distance": obj["close_approach_data"][0]["miss_distance"],
                            "close_approach_date": obj["close_approach_data"][0]["close_approach_date"]
                        }] if obj.get("close_approach_data") else []
                    })
            
            return simplified_data
        except Exception as e:
            return {"error": f"Failed to fetch NASA data: {str(e)}"}

async def calculate_asteroid_kinetic_energy(diameter_km: float, velocity_km_s: float, density_kg_m3: float = 3000) -> dict:
    """
    Calculates the estimated kinetic energy of an asteroid impact in Megatons of TNT.
    Formula: E = 0.5 * mass * velocity^2
    Mass is estimated using the diameter and assumed density (default 3000 kg/m3 for stony asteroids).
    """
    import math
    try:
        # Radius in meters
        radius_m = (diameter_km * 1000) / 2
        # Volume in m3
        volume_m3 = (4/3) * math.pi * (radius_m**3)
        # Mass in kg
        mass_kg = volume_m3 * density_kg_m3
        # Velocity in m/s
        velocity_m_s = velocity_km_s * 1000
        # Energy in Joules
        energy_j = 0.5 * mass_kg * (velocity_m_s**2)
        # Convert to Megatons (1 Mt = 4.184e15 Joules)
        energy_mt = energy_j / 4.184e15
        
        return {
            "mass_kg": f"{mass_kg:.2e}",
            "impact_energy_mt": f"{energy_mt:.2f} Megatons",
            "comparison": "Hiroshima bomb was ~0.015 Mt. Tsar Bomba was ~50 Mt."
        }
    except Exception as e:
        return {"error": f"Calculation failed: {str(e)}"}
async def get_historical_impact_data() -> dict:
    """
    Returns a reference dataset of famous historical asteroid impact events
    for comparison with current threats.
    """
    return {
        "Chelyabinsk (2013)": {
            "diameter_m": 20,
            "velocity_km_s": 19,
            "impact_energy_mt": 0.5,
            "description": "Exploded over Russia, causing wide-spread minor injuries and glass damage."
        },
        "Tunguska (1908)": {
            "diameter_m": 50,
            "velocity_km_s": 15,
            "impact_energy_mt": 15,
            "description": "Flattened 2000 sq km of forest in Siberia. No crater (airburst)."
        },
        "Chicxulub (KT Extinction)": {
            "diameter_km": 10,
            "velocity_km_s": 20,
            "impact_energy_mt": 100000000,
            "description": "Ended the era of dinosaurs. Global climate catastrophe."
        },
        "Barringer Crater (Meteor Crater)": {
            "diameter_m": 50,
            "velocity_km_s": 12.8,
            "impact_energy_mt": 10,
            "description": "Created the iconic 1.2km wide crater in Arizona ~50,000 years ago."
        }
    }
