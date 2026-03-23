import os
import asyncio
from google.adk.agents import Agent, LoopAgent
from google.adk.tools import FunctionTool
from tools.nasa_tools import fetch_neo_data_func, calculate_asteroid_kinetic_energy, get_historical_impact_data
from tools.python_tool import python_interpreter_func

# System Constants
PROJECT_ID = "adk-beta-1"
MODEL_ID = "gemini-2.5-flash-lite"
LOCATION = "us-central1"

# Force Vertex AI for project context
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION

# Step 1: Wrap functions in FunctionTool
fetch_neo_tool = FunctionTool(fetch_neo_data_func)
python_tool = FunctionTool(python_interpreter_func)
kinetic_tool = FunctionTool(calculate_asteroid_kinetic_energy)
historical_tool = FunctionTool(get_historical_impact_data)

# Step 2: Define the Data Specialist
data_specialist = Agent(
    name="DataSpecialist",
    model=MODEL_ID,
    description="Expert at fetching NASA Near-Earth Object data.",
    instruction="""
    1. CHECK CONTEXT: If NASA telemetry is already in the history, DO NOT CALL THE TOOL. Move to the next agent.
    2. MISSION: Only fetch asteroid data via fetch_neo_data if it's missing.
    3. HANDOFF: Provide the telemetry raw and exit.
    """,
    tools=[fetch_neo_tool]
)

# Step 3: Define the Analysis Specialist
analysis_specialist = Agent(
    name="AnalysisSpecialist",
    model=MODEL_ID,
    description="Python expert that calculates kinetic energy and evaluates threat benchmarks.",
    instruction="""
    SYSTEM ROLE: STRATEGIC THREAT ANALYST.
    1. MISSION: Perform kinetic energy analysis (0.5mv²) for top 3 threats using calculate_asteroid_kinetic_energy.
    2. HISTORICAL EQUIVALENCE: Use get_historical_impact_data to benchmark threats.
       - TUNGUSKA LEVEL = 15 Megatons.
       - CHELYABINSK LEVEL = 0.5 Megatons.
    3. PROBABILITY/ASSESSMENT: If the user asks for "probability" or "risk", provide a 'Threat Equivalence' assessment. 
       - E.g., "The current primary threat is 10x the energy of Tunguska, representing a critical risk."
    4. TACTICAL: Use python_interpreter for advanced unit conversions (e.g., Megatons to Hiroshimas).
    5. PRECISION: Provide results in Markdown and STOP.
    """,
    tools=[kinetic_tool, python_tool, historical_tool]
)

# Step 4: Define the Briefing Specialist
briefing_specialist = Agent(
    name="BriefingSpecialist",
    model=MODEL_ID,
    description="Military communications expert who summarizes threat tables into urgent executive briefings.",
    instruction="""
    SYSTEM ROLE: STRATEGIC COMMUNICATIONS.
    1. MISSION: Convert the analysis table into an urgent 3-point SITREP in ALL CAPS.
    2. TACTICAL: If the AnalysisSpecialist provided a historical comparison (Tunguska/Chelyabinsk), make sure to emphasize it.
    3. SIGNAL: Conclude with "--- MISSION COMPLETE ---" for the initial scan.
    4. FINAL: Once the response is delivered, state "TASK_FINISHED" to close the channel.
    """,
)

# Step 5: Define the Commander (LoopAgent) - Factory Pattern for Continuity
async def get_commander_agent(user_email: str):
    # Retrieve previous mission context for continuity
    prev_context = await get_last_mission_context(user_email)
    
    # Return a fresh LoopAgent with continuity awareness
    return LoopAgent(
        name="NEOCommander",
        description="Main orchestrator for the NEO Threat Board. Coordinates Data -> Analysis -> Briefing flow.",
        sub_agents=[data_specialist, analysis_specialist, briefing_specialist],
        max_iterations=3,
        instruction=f"""
        SYSTEM ROLE: LEAD TACTICAL COMMANDER.
        
        NEURAL LINK CONTINUITY: 
        Maintain situational awareness from previous missions. 
        {f"Your last mission report concluded with: {prev_context}" if prev_context else "No prior mission data. This is a cold start."}
        
        GOAL: Orchestrate specialist agents to fulfill the user's order.
        1. INITIALIZE: Call DataSpecialist to fetch current telemetry.
        2. ANALYZE: Call AnalysisSpecialist for kinetic/historical benchmarks.
        3. SUMMARY: Call BriefingSpecialist for the final urgent SITREP.
        
        PRECISION: Once a Final SITREP is produced, STOP and conclude the mission.
        """
    )
