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
    1. MISSION: Fetch asteroid data for the next 7 days using fetch_neo_data. 
    2. TACTICAL: If the user asks for specific object info, use fetch_neo_data for the relevant window.
    3. HANDOFF: Pass raw data to the team. No conversational intros.
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
    1. MISSION: By default, calculate kinetic energy for the top 3 high-risk objects using calculate_asteroid_kinetic_energy and generate a Markdown table.
    2. TACTICAL: If the user issues a specific calculation order (e.g. Lunar Distances, velocity comparisons, or hypothetical scenarios), prioritize that calculation using the python_interpreter.
    3. PRECISION: Provide exact values from the telemetry. STOP after your analysis is complete.
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
    description="Main orchestrator for the NEO Threat Board.",
    instruction="""
    GOAL: COORDINATE THREAT ASSESSMENTS.
    1. DEFAULT: Start with a full 7-day telemetry scan (Data -> Analysis -> Briefing).
    2. TACTICAL ORDERS: If the user issues a specific command or follow-up, task the appropriate specialist and respond immediately.
    3. FLOW: Maintain a crisp military protocol. Exit the loop when the objective is met.
    """,
    sub_agents=[data_specialist, analysis_specialist, briefing_specialist],
    max_iterations=4
)
