import asyncio
from agent.commander import commander_agent

async def test_scenarios():
    print("--- SCENARIO 1: Identity Generation ---")
    resp1 = await commander_agent.run("I am a new survivor named 'Kael'. I wear a dark blue suit with neon highlights. Generate my portrait.")
    print(f"Commander: {resp1.text}\n")

    print("--- SCENARIO 2: Planet Data ---")
    resp2 = await commander_agent.run("What are the hazards in the Volcanic biome?")
    print(f"Commander: {resp2.text}\n")

    print("--- SCENARIO 3: SOS Processing ---")
    resp3 = await commander_agent.run("Incoming report: 'Survivor Sarah here. Low on water in the Cryo biome. Priority Alpha.'")
    print(f"Commander: {resp3.text}\n")

    print("--- SCENARIO 4: Consensus Decision ---")
    resp4 = await commander_agent.run("Should we attempt a rescue in the Bioluminescent area tonight or wait for dawn?")
    print(f"Commander: {resp4.text}\n")

if __name__ == "__main__":
    asyncio.run(test_scenarios())
