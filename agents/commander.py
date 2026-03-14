import os
from google.adk.agents import Agent, LoopAgent
from google.adk.tools import FunctionTool
from tools.nasa_tools import fetch_neo_data_func
from tools.python_tool import python_interpreter_func

# Force Vertex AI for adk-beta-1 project
os.environ["GOOGLE_CLOUD_PROJECT"] = "adk-beta-1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# Step 1: Wrap functions in FunctionTool
fetch_neo_tool = FunctionTool(fetch_neo_data_func)
python_tool = FunctionTool(python_interpreter_func)

# Step 2: Define the Data Specialist
data_specialist = Agent(
    name="DataSpecialist",
    model="gemini-2.5-flash",
    description="Expert at fetching NASA Near-Earth Object data.",
    instruction="""
    1. Fetch asteroid data for the next 7 days using the fetch_neo_data tool.
    2. If successful, pass the raw JSON to the next agent.
    3. If there is an API error or no data, explain the failure so the commander can decide how to recover.
    """,
    tools=[fetch_neo_tool]
)

# Step 3: Define the Analysis Specialist
analysis_specialist = Agent(
    name="AnalysisSpecialist",
    model="gemini-2.5-flash",
    description="Python expert that calculates kinetic energy and threat levels.",
    instruction="""
    SYSTEM ROLE: You are a KINETIC ENERGY ANALYST.
    1. READ THE CONTEXT: Locate the 'near_earth_objects' JSON data.
    2. CALL TOOL: Use python_interpreter IMMEDIATELY. Do not list asteroids in text first.
    3. YOUR CODE MUST:
       - Loop through all dates and asteroids.
       - Calculate mass = (4/3) * pi * (avg_radius^3) * 2000.
       - Calculate Kinetic Energy = 0.5 * mass * (velocity_mps^2).
       - Create a list of objects with {'name', 'energy', 'diameter', 'velocity'}.
       - Sort by energy descending.
    4. FINAL OUTPUT: Print ONLY the Markdown table and 'MISSION COMPLETE'. No conversational filler.
    """,
    tools=[python_tool]
)

# Step 4: Define the Briefing Specialist (New Wow Factor)
briefing_specialist = Agent(
    name="BriefingSpecialist",
    model="gemini-2.5-flash",
    description="Military communications expert who summarizes threat tables into urgent executive briefings.",
    instruction="""
    SYSTEM ROLE: STRATEGIC COMMUNICATIONS.
    1. READ THE CONTEXT: Locate the high-risk objects from AnalysisSpecialist.
    2. IMMEDIATE ACTION: Generate a 3-bullet point "FLASH SITREP". 
    3. STYLE: Urgent, military, ALL CAPS for impact. 
    4. NO FILLER: Start with **CRITICAL THREAT ALERT** and end with **END TRANSMISSION**.
    """,
)

# Step 5: Define the Commander (LoopAgent)
# LoopAgent is an orchestrator that runs sub-agents in a loop until one escalates or max_iterations reached.
commander_agent = LoopAgent(
    name="NEOCommander",
    description="Main orchestrator for the NEO Threat Board.",
    sub_agents=[data_specialist, analysis_specialist, briefing_specialist],
    max_iterations=6
)
