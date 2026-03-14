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

@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")

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
async def stream_assessment(user_query: str = "Identify major NEO threats", session_id: str = "neo_live_stream"):
    """
    Streams the LoopAgent's reasoning steps and tool outputs as SSE.
    """
    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # Critical for Nginx/Cloud Run responsiveness
    }

    async def event_generator():
        from google.genai import types
        
        # Immediate Heartbeat
        yield f"data: {json.dumps({'type': 'log', 'content': '📡 NEURAL LINK ESTABLISHED. INITIALIZING ENGINE...'})}\n\n"

        runner = Runner(
            app_name="NEOThreatTracker",
            agent=commander_agent,
            session_service=session_service,
            artifact_service=artifact_service,
            auto_create_session=True
        )
        
        try:
            print(f"DEBUG: Starting assessment for query: {user_query} | Session: {session_id}")
            async for event in runner.run_async(
                user_id="demo_user", 
                session_id=session_id,
                new_message=types.UserContent(parts=[types.Part(text=user_query)])
            ):
                content_str = ""
                event_type = "log"
                
                # Extract content from parts
                if hasattr(event, "content") and event.content and hasattr(event.content, "parts"):
                    for p in event.content.parts:
                        # 1. Text
                        if hasattr(p, "text") and p.text:
                            content_str += p.text
                            
                        # 2. Function Call
                        elif hasattr(p, "function_call") and p.function_call:
                            content_str += f"\n🚀 EXECUTING TOOL: {p.function_call.name}"
                            
                        # 3. Function Response (Telemetry)
                        elif hasattr(p, "function_response") and p.function_response:
                            resp = p.function_response
                            if resp.name == "fetch_neo_data_func":
                                tel_content = resp.response
                                if isinstance(tel_content, str):
                                    try: tel_content = json.loads(tel_content)
                                    except: pass
                                yield f"data: {json.dumps({'type': 'telemetry', 'content': tel_content})}\n\n"
                                content_str += "\n📡 SENSOR DATA RECEIVED. ASSEMBLING THREAT TABLE..."
                            else:
                                content_str += f"\n✅ Tool {resp.name} completed."
                
                if not content_str.strip():
                    # Send a heartbeat if there's no visible content yet
                    yield f"data: {json.dumps({'type': 'log', 'content': '...'})}\n\n"
                    continue
                    
                yield f"data: {json.dumps({'type': 'log', 'content': content_str.strip()})}\n\n"
                await asyncio.sleep(0.01) # Ultra-fast flush
                
        except Exception as e:
            import traceback
            error_msg = f"Agent Error: {str(e)}"
            print(f"ERROR: {error_msg}\n{traceback.format_exc()}")
            yield f"data: {json.dumps({'type': 'log', 'content': f'⚠️ {error_msg}'})}\n\n"

    return StreamingResponse(event_generator(), headers=headers, media_type="text/event-stream")

@app.post("/chat")
async def chat(request: Request):
    return {"status": "Use /stream-assessment?user_query=... for interactive chat"}



if __name__ == "__main__":
    import uvicorn
    # Use 8080 as standard for Cloud Run
    uvicorn.run(app, host="0.0.0.0", port=8080)
