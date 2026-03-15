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
    1. CHECK CONTEXT: If NASA telemetry is already in the history, DO NOT CALL THE TOOL. Move to the next agent.
    2. MISSION: Only fetch asteroid data via fetch_neo_data if it's missing.
    3. HANDOFF: Provide the telemetry raw and exit.
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
    1. CHECK CONTEXT: If a threat table already exists, DO NOT recalculate unless asked.
    2. MISSION: Perform kinetic energy analysis (0.5mv²) for top 3 threats using calculate_asteroid_kinetic_energy.
    3. TACTICAL: Prioritize specific user math (Lunar Distances, hypotheticals) using python_interpreter.
    4. PRECISION: Provide results in Markdown and STOP immediately.
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
    1. MISSION: Convert the analysis table into an urgent 3-point SITREP in ALL CAPS.
    2. TACTICAL: If responding to a specific question or tactical order, provide a direct, concise answer instead of a 3-point SITREP.
    3. SIGNAL: Conclude with "--- MISSION COMPLETE ---" for the initial scan.
    4. FINAL: Once the response is delivered, state "TASK_FINISHED" to close the channel.
    """,
)

# Step 5: Define the Commander (LoopAgent)
commander_agent = LoopAgent(
    name="NEOCommander",
    description="Main orchestrator for the NEO Threat Board. Coordinates Data -> Analysis -> Briefing flow.",
    sub_agents=[data_specialist, analysis_specialist, briefing_specialist],
    max_iterations=3  # Reduced for faster termination/demo stability
)
