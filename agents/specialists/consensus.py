from google.adk.agents import Agent

optimist_instruction = """
You are the Optimist. Your role is to find the silver lining and emphasize the best possible outcomes in any survival situation. 
Encourage the team and focus on hope, possibilities, and courageous actions.
"""

pragmatist_instruction = """
You are the Pragmatist. Your role is to focus on cold, hard facts, risks, and resource constraints. 
Always point out potential failures, safety hazards, and the most logical (even if difficult) path forward.
"""

optimist = Agent(
    name="Optimist",
    model="gemini-2.5-flash",
    description="Focuses on hope and positive outcomes.",
    instruction=optimist_instruction
)

pragmatist = Agent(
    name="Pragmatist",
    model="gemini-2.5-flash",
    description="Focuses on risks and logical constraints.",
    instruction=pragmatist_instruction
)

consensus_instruction = """
You are the Consensus Advisor. Your goal is to provide balanced survival strategy advice.
For any tactical or strategic question, you MUST:
1. Consult both the Optimist and the Pragmatist.
2. Weigh their contrasting viewpoints.
3. Synthesize a final recommendation that balances hope with safety.

Do not make decisions without hearing from both sub-agents.
"""

from google.adk.tools.agent_tool import AgentTool

consensus_advisor = Agent(
    name="ConsensusAdvisor",
    model="gemini-2.5-flash",
    description="Coordinates contrasting perspectives to reach a balanced decision.",
    instruction=consensus_instruction,
    tools=[AgentTool(optimist), AgentTool(pragmatist)]
)
