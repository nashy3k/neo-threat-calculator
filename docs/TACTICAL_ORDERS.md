# 🛰️ NEO Commander: Tactical Order Manual

This guide provides a curated list of commands to showcase the **NEO Threat Calculator** during the 150-second demo. 

## 🎬 Recommended Demo Script (150s Pitch)

**Phase 1: Initialization**
1.  **Click [INITIALIZE SEQUENCE]**
    *   *Purpose*: Populates the dashboard with real NASA telemetry. Showcases the 100% scrollable panels and the Neural Link visualization.

**Phase 2: Deep Analysis (30s - 90s)**
2.  **Order**: `"Run a kinetic energy assessment on the top 3 hazardous objects."`
    *   *Agent Reaction*: The `AnalysisSpecialist` will calculate potential impact energy in Megatons (Tnt) in the logs.
3.  **Order**: `"Identify the object with the highest relative velocity and calculate its minimum miss distance in Lunar Distances."`
    *   *Agent Reaction*: Showcases the ability to filter and perform specific geometric math using Python.

**Phase 3: Adaptive Memory & Narrative (90s - 150s)**
4.  **Order**: `"Focus on the fastest object from the previous scan. What happens if its distance to Earth is halved?"`
    *   *Agent Reaction*: **STRENGTH**: The agent remembers which object was the fastest. It performs a hypothetical calculation.
5.  **Order**: `"Generate a final FLASH SITREP for the High Command."`
    *   *Agent Reaction*: Triggers the `BriefingSpecialist`. Look for the **ORANGE LOGS** for high-impact visual storytelling.

---

## 🛠️ Advanced Tactical Commands

Use these to show off the range of the agentic engine:

### 🔬 Mathematical & Geometric
- `"Calculate the escape velocity required to divert the largest asteroid by 5 degrees."`
- `"Rank all SAFE asteroids by their estimated mass, assuming a standard iron-nickel density."`
- `"What is the probability of a Tunguska-level event based on the current 7-day telemetry?"`

### 🧠 Memory & Reasoning
- `"Compare the kinetic energy of the current primary threat to the Chelyabinsk meteor."`
- `"Filter the dashboard for only objects with a diameter greater than 0.5km."`
- `"If we launched a kinetic impactor today, how long until interception with object [NAME]?"`

### 📢 Strategic narrative
- `"Issue a Stage 2 Planetary Defense Alert for all hazardous detections."`
- `"Prepare a technical summary for a non-expert audience (Scenario: Civilian Broadcast)."`
- `"Translate the current threat board into a Morse Code transmission (Demo: Low-bandwidth Comm Link)."`

---

> [!TIP]
> **Demo Pro-Tip**: When the agent is "Thinking", use the time to point at the **API Loop Counter** in the header to explain that you are using a LoopAgent architecture to handle multi-step reasoning.
