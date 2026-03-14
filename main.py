from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from agents.commander import commander_agent
import os
import json
import asyncio

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="NEO Threat Tracker")

# Mount frontend
app.mount("/static", StaticFiles(directory="app"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "operational", "project": "adk-beta-1", "agent": "NEOCommander"}

# Global persistent services for in-memory session memory
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

@app.get("/stream-assessment")
async def stream_assessment(user_query: str = "Identify major NEO threats"):
    """
    Streams the LoopAgent's reasoning steps and tool outputs as SSE.
    """
    async def event_generator():
        from google.genai import types

        # Use the base Runner class to allow custom session/artifact services
        runner = Runner(
            app_name="NEOThreatTracker",
            agent=commander_agent,
            session_service=session_service,
            artifact_service=artifact_service,
            auto_create_session=True
        )
        
        try:
            async for event in runner.run_async(
                user_id="demo_user", 
                session_id="neo_live_stream",
                new_message=types.UserContent(parts=[types.Part(text=user_query)])
            ):
                content_str = ""
                # Extract text if it's a model message
                if hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts"):
                        content_str = "".join([p.text for p in event.content.parts if hasattr(p, 'text') and p.text])
                
                # Extract tool calls/actions for better visualization
                if hasattr(event, "actions"):
                    actions = event.actions
                    # Handle Tool Responses (This is the Telemetry!)
                    if hasattr(actions, "function_responses") and actions.function_responses:
                        for resp in actions.function_responses:
                            if resp.name == "get_asteroids":
                                # Safely serialize the telemetry data
                                try:
                                    # If it's a string, try to parse first, then re-serialize
                                    tel_content = resp.response
                                    if isinstance(tel_content, str):
                                        try: tel_content = json.loads(tel_content)
                                        except: pass
                                    
                                    yield f"data: {json.dumps({'type': 'telemetry', 'content': tel_content})}\n\n"
                                    print(f"📡 Telemetry relayed for: {resp.name}")
                                except Exception as json_err:
                                    print(f"Error serializing telemetry: {json_err}")
                                    
                        content_str = "📡 TELEMETRY RECEIVED. ANALYZING OBJECT DATA..."
                    
                    # Handle Tool Calls
                    elif hasattr(actions, "function_calls") and actions.function_calls:
                        content_str = f"🚀 EXECUTING: {actions.function_calls[0].name}"

                if not content_str:
                    continue # Skip empty control events to keep log clean
                    
                data = {
                    "type": "log",
                    "content": content_str
                }
                yield f"data: {json.dumps(data)}\n\n"
                await asyncio.sleep(0.02) # Snappy streaming
        except Exception as e:
            import traceback
            error_msg = f"Agent Error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg[:500]})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/chat")
async def chat(request: Request):
    return {"status": "Use /stream-assessment?user_query=... for interactive chat"}



if __name__ == "__main__":
    import uvicorn
    # Use 8080 as standard for Cloud Run
    uvicorn.run(app, host="0.0.0.0", port=8080)
