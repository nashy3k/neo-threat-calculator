# Master Brain: Hackathon Strategy ("Way Back Home")

This document synthesizes our research (Colabs) and practical application (Workshop Levels) into a unified strategy for the hackathon.

---

## 🛠️ Core Technology Stack
- **Orchestration**: **Google ADK** (Sequential, Parallel, Loop, and Workflow agents).
- **LLM Selection**: **Gemini 2.5 Flash** (Balanced speed/reasoning) or **Local Gemma 2** (Privacy/Local dev).
- **Data Tools**: **BigQuery** (Structured), **Vertex Search** (Unstructured), **Document Analysis** (Files).
- **Search**: **Hybrid Search** (Routing between Keyword filters and Semantic RAG).
- **Safety**: **Multi-layered** (Gemini built-in filters + Agent-based halluncination graders).

---

## 🏗️ Architectural Patterns & Track Alignment
| Pattern | Alignment | Source | Use Case |
| :--- | :--- | :--- | :--- |
| **Research Swarm** | **Track A** | Level 1 / Search | Strategic synthesis of unstructured data. |
| **Data Swarm** | **Track B** | `ai-agents-adk` | Autonomous Python execution for computation. |
| **Process Swarm** | **Track C** | `travel_hub` | Orchestrating APIs and real-world workflows. |
| **Workflow (Linear)** | Tracks B/C | `SequentialAgent` | Deterministic multi-step data or task pipelines. |
| **Streaming (Live)** | All Tracks | `way-back-home` | Real-time voice/image interaction interface. |
| **MCP Integration** | Track C | `currency-agent` | Connecting to standardized external tool servers. |
| **A2A / Multi-Agent** | Track C | `way-back-home` | Decentralized multi-agent rescue/ops coordination. |
| **Reasoning Loops** | Track B | `LoopAgent` | Self-correcting code and data analysis cycles. |

---

## ⚖️ Judging Criteria (Priority)
1. **Agentic Agency & Recovery (40%)**: The system's ability to reason, correct itself, and recover from tool/API failures.
2. **Technical Depth (30%)**: Complexity of agent graphs, tool usage, and prompt engineering.
3. **System Robustness (20%)**: Reliable performance, error handling, and latency management.
4. **Docs & Demo (10%)**: Clear explanation of the mission and a WOW-factor demonstration.

## 💡 Key Design Principles
1. **Latency Optimization**: Direct routing (Keyword/Semantic) is preferred over expensive Hybrid Search unless intent is ambiguous.
2. **Character Continuity**: Use multi-turn session context to maintain visual and behavioral consistency (Level 0).
3. **Transparent Reasoning**: Always show the agent's "Search Strategy" or "Consensus Logic" to build user trust.
4. **Resiliency**: Schedule sensitive tasks (like memory persistence) using background `asyncio` tasks to prevent UI blocking.

---

## 🚀 Hackathon Readiness
- **Templates Available**: `SequentialAgent` for RAG pipelines, `ParallelAgent` for consensus analysis.
- **Tools Ready**: Multimedia extraction sub-agents, Memory Bank callbacks, and Hybrid Search interpreters.

---

## 🎙️ Pitch & Documentation Prep (NotebookLLM)
- **Strategy**: Creating a sub-agent to navigate NotebookLLM's web UI is fragile due to Google Auth requirements. Instead, the Antigravity agent will automatically generate a **"NotebookLLM Source Kit"** (an organized folder of Markdown summaries, architectural schemas, and WOW-factor explanations).
- **Execution**: The user simply drags-and-drops this `notebook_llm_kit` folder into a new NotebookLLM project to instantly generate the "Audio Overview" (Podcast) and pitch guides for the judges.
