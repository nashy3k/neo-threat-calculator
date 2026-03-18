from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from agents.commander import commander_agent
import os
import json
import asyncio

from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from config.secrets import get_secret
from config.auth import oauth, verify_auth
from fastapi import Depends

app = FastAPI(title="NEO Threat Tracker")

# Mount frontend
app.mount("/static", StaticFiles(directory="app"), name="static")

# Tier 1 Security: Session Management
app.add_middleware(
    SessionMiddleware, 
    secret_key=get_secret("SESSION_SECRET_KEY"),
    max_age=3600  # 1 hour session
)

# Tier 2 Security: Restrictive CORS
# Only allow Localhost for development and *.a.run.app for production
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|.*\.a\.run\.app)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")

@app.get("/login")
async def login(request: Request):
    # Ensure the redirect URI uses https if on Cloud Run
    redirect_uri = request.url_for('auth')
    if "a.run.app" in str(redirect_uri):
        redirect_uri = str(redirect_uri).replace("http://", "https://")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/')

@app.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

@app.get("/user")
async def get_user(request: Request):
    user = request.session.get('user')
    return {"authenticated": user is not None, "user": user}

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
async def stream_assessment(
    user_query: str = "Identify major NEO threats", 
    session_id: str = "neo_live_stream",
    user: dict = Depends(verify_auth) # PROTECTED
):
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
        import datetime
        
        # 1. Pump Priming: Force Cloud Run/Proxies to flush the stream immediately
        # We send a larger invisible comment block (4KB) to overcome common proxy buffers
        yield f": {' ' * 4096}\n\n"
        
        def get_ts():
            return datetime.datetime.now().strftime("%H:%M:%S")

        # Immediate Heartbeat with Server Timestamp
        yield f"data: {json.dumps({'type': 'log', 'content': '📡 NEURAL LINK ESTABLISHED. INITIALIZING ENGINE...', 'server_time': get_ts()})}\n\n"
        await asyncio.sleep(0.01) # Force flush

        runner = Runner(
            app_name="NEOThreatTracker",
            agent=commander_agent,
            session_service=session_service,
            artifact_service=artifact_service,
            auto_create_session=True
        )
        
        try:
            print(f"DEBUG: Starting assessment for query: {user_query} | Session: {session_id}")
            current_role = "system" # Persistent role tracking
            
            async for event in runner.run_async(
                user_id="demo_user", 
                session_id=session_id,
                new_message=types.UserContent(parts=[types.Part(text=user_query)])
            ):
                content_str = ""
                
                # Robust Agent Role Identification (Scavenger Hunt)
                agent_name = None
                
                # Case 1: event itself is an agent-like object or has .agent
                if hasattr(event, "agent") and event.agent:
                    agent_name = getattr(event.agent, "name", None)
                # Case 2: event has agent_turn
                elif hasattr(event, "agent_turn") and event.agent_turn:
                    turn_agent = getattr(event.agent_turn, "agent", None)
                    if turn_agent:
                        agent_name = getattr(turn_agent, "name", None)
                # Case 3: event has a name (some events are the agent objects themselves)
                elif hasattr(event, "name") and not hasattr(event, "content"):
                    agent_name = event.name
                
                # Case 4: Nuclear Option - check str representation for specialist names
                if not agent_name:
                    ev_str = str(event)
                    if "BriefingSpecialist" in ev_str: agent_name = "BriefingSpecialist"
                    elif "AnalysisSpecialist" in ev_str: agent_name = "AnalysisSpecialist"
                    elif "DataSpecialist" in ev_str: agent_name = "DataSpecialist"
                    elif "NEOCommander" in ev_str: agent_name = "NEOCommander"

                if agent_name:
                    if agent_name == "BriefingSpecialist":
                        current_role = "briefing"
                        print("DEBUG: Active Agent -> BriefingSpecialist")
                    elif agent_name in ["DataSpecialist", "AnalysisSpecialist"]:
                        current_role = "research"
                        print(f"DEBUG: Active Agent -> {agent_name}")
                    elif agent_name == "NEOCommander":
                        current_role = "system"
                        print("DEBUG: Active Agent -> NEOCommander")

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
                            if resp.name in ["fetch_neo_data_func", "calculate_asteroid_kinetic_energy"]:
                                tel_content = resp.response
                                if isinstance(tel_content, str):
                                    try: tel_content = json.loads(tel_content)
                                    except: pass
                                yield f"data: {json.dumps({'type': 'telemetry', 'content': tel_content})}\n\n"
                                
                                if resp.name == "fetch_neo_data_func":
                                    content_str += "\n📡 SENSOR DATA RECEIVED. ASSEMBLING THREAT TABLE..."
                                else:
                                    content_str += "\n⚡ KINETIC CALCULATIONS COMPLETE. THREAT LEVEL QUANTIFIED."
                            else:
                                content_str += f"\n✅ Tool {resp.name} completed."
                
                if not content_str.strip():
                    # Pass the current role to heartbeats
                    # We only send these if the runner is actually doing something (avoid flooding)
                    yield f"data: {json.dumps({'type': 'log', 'content': '...', 'role': current_role, 'server_time': get_ts()})}\n\n"
                    continue
                    
                yield f"data: {json.dumps({'type': 'log', 'content': content_str.strip(), 'role': current_role, 'server_time': get_ts()})}\n\n"
                await asyncio.sleep(0.01) # Ultra-fast flush
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
