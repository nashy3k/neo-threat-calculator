import os
from google.adk.agents import Agent, LoopAgent
from google.adk.tools import FunctionTool
from tools.nasa_tools import fetch_neo_data_func, calculate_asteroid_kinetic_energy
from tools.python_tool import python_interpreter_func

# Force Vertex AI for adk-beta-1 project
os.environ["GOOGLE_CLOUD_PROJECT"] = "adk-beta-1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# Step 1: Wrap functions in FunctionTool
fetch_neo_tool = FunctionTool(fetch_neo_data_func)
python_tool = FunctionTool(python_interpreter_func)
kinetic_tool = FunctionTool(calculate_asteroid_kinetic_energy)

# Step 2: Define the Data Specialist
data_specialist = Agent(
    name="DataSpecialist",
    model="gemini-2.5-flash",
    description="Expert at fetching NASA Near-Earth Object data.",
    instruction="""
    1. Fetch asteroid data for the next 7 days using fetch_neo_data.
    2. Pass the raw results to the next specialist. Do not repeat this after the first successful fetch.
    """,
    tools=[fetch_neo_tool]
)

# Step 3: Define the Analysis Specialist
analysis_specialist = Agent(
    name="AnalysisSpecialist",
    model="gemini-2.5-flash",
    description="Python expert that calculates kinetic energy and threat levels.",
    instruction="""
    SYSTEM ROLE: KINETIC ENERGY ANALYST.
    1. READ DATA: Look for asteroid proximity data.
    2. CALCULATE: Use calculate_asteroid_kinetic_energy for the top 3 fastest/largest objects.
    3. SUMMARY: Generate a Markdown table with Name, Velocity, and Impact Energy (MT).
    4. NO FILLER: STOP after generating the table.
    """,
    tools=[kinetic_tool, python_tool]
)

# Step 4: Define the Briefing Specialist
briefing_specialist = Agent(
    name="BriefingSpecialist",
    model="gemini-2.5-flash",
    description="Military communications expert who summarizes threat tables into urgent executive briefings.",
    instruction="""
    SYSTEM ROLE: STRATEGIC COMMUNICATIONS.
    1. ACTION: Convert AnalysisSpecialist's table into an urgent SITREP.
    2. LIMIT: EXACTLY 3 bullet points. No more.
    3. TERMINATION: Conclude with "--- MISSION COMPLETE ---".
    4. FINAL: Once the SITREP is delivered, state "TASK_FINISHED" clearly to signal the end of the operation.
    """,
)

# Step 5: Define the Commander (LoopAgent)
commander_agent = LoopAgent(
    name="NEOCommander",
    description="Main orchestrator for the NEO Threat Board.",
    instruction="""
    GOAL: COORDINATE A SINGLE THREAT ASSESSMENT MISSION.
    1. Task DataSpecialist to get telemetry.
    2. Task AnalysisSpecialist to calculate energies.
    3. Task BriefingSpecialist to issue the Sitrep.
    4. STOP immediately after the BriefingSpecialist is done. Do not repeat the loop.
    """,
    sub_agents=[data_specialist, analysis_specialist, briefing_specialist],
    max_iterations=4 # Cap iterations to prevent hangs
)
