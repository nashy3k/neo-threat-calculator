import asyncio
import json
from google.genai import types
from google.adk.runners import Runner
from agents.commander import commander_agent
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService

async def main():
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    
    runner = Runner(
        app_name="NEOThreatTracker",
        agent=commander_agent,
        session_service=session_service,
        artifact_service=artifact_service,
        auto_create_session=True
    )
    
    print("Testing NEO sequence...")
    async for event in runner.run_async(
        user_id="test", 
        session_id="neo_test_2",
        new_message=types.UserContent(parts=[types.Part(text="Find high risk asteroids in the next 7 days")])
    ):
        content_str = ""
        
        if hasattr(event, "content") and event.content and hasattr(event.content, "parts"):
            for p in event.content.parts:
                if hasattr(p, "text") and p.text:
                    content_str += p.text
                elif hasattr(p, "function_call") and p.function_call:
                    content_str += f"\n🚀 EXECUTING TOOL: {p.function_call.name}"
                elif hasattr(p, "function_response") and p.function_response:
                    content_str += f"\n✅ TOOL RESPONSE RECEIVED: {p.function_response.name}"
                    if p.function_response.name == "fetch_neo_data_func":
                        print(">>> TELEMETRY DETECTED <<<")
                    
        if not content_str.strip():
            print(">>> EVENT YIELDED NO CONTENT (fallback to '...')")
        else:
            print(f"OUTPUT: {content_str.strip()}")

if __name__ == "__main__":
    asyncio.run(main())
