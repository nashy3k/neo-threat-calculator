from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types
import os
import json
import asyncio
import datetime

from config.secrets import get_secret
from config.auth import oauth, verify_auth, get_allowed_users
from config.database import log_user_login, log_mission_trace
from agents.commander import commander_agent, PROJECT_ID, MODEL_ID

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
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|.*\.a\.run\.app)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
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
        # [NEW] Log the login event to Firestore for auditing
        log_user_login(user['email'], request.client.host)
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
    return {"status": "operational", "project": PROJECT_ID, "agent": "NEOCommander"}

@app.get("/info")
async def get_info():
    return {
        "project": PROJECT_ID,
        "model": MODEL_ID.upper(),
        "version": "1.2.0-ALBETA"
    }

# Global persistent services for in-memory session memory
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
        # 1. Pump Priming: Force Cloud Run/Proxies to flush the stream immediately
        yield f": {' ' * 4096}\n\n"
        
        def get_ts():
            return datetime.datetime.now().strftime("%H:%M:%S")

        yield f"data: {json.dumps({'type': 'log', 'content': '📡 NEURAL LINK ESTABLISHED. INITIALIZING ENGINE...', 'server_time': get_ts()})}\n\n"
        await asyncio.sleep(0.01)

        runner = Runner(
            app_name="NEOThreatTracker",
            agent=commander_agent,
            session_service=session_service,
            artifact_service=artifact_service,
            auto_create_session=True
        )
        
        mission_trace_events = [] # For logging the full trace to Firestore
        user_email = user.get('email', 'anonymous')
        
        try:
            current_role = "system"
            async for event in runner.run_async(
                user_id="demo_user", 
                session_id=session_id,
                new_message=types.UserContent(parts=[types.Part(text=user_query)])
            ):
                content_str = ""
                agent_name = None
                
                # Role Identification
                if hasattr(event, "agent") and event.agent:
                    agent_name = getattr(event.agent, "name", None)
                elif hasattr(event, "agent_turn") and event.agent_turn:
                    turn_agent = getattr(event.agent_turn, "agent", None)
                    if turn_agent: agent_name = getattr(turn_agent, "name", None)
                elif hasattr(event, "name") and not hasattr(event, "content"):
                    agent_name = event.name
                
                if not agent_name:
                    ev_str = str(event)
                    if "BriefingSpecialist" in ev_str: agent_name = "BriefingSpecialist"
                    elif "AnalysisSpecialist" in ev_str: agent_name = "AnalysisSpecialist"
                    elif "DataSpecialist" in ev_str: agent_name = "DataSpecialist"
                    elif "NEOCommander" in ev_str: agent_name = "NEOCommander"

                if agent_name:
                    if agent_name == "BriefingSpecialist":
                        current_role = "briefing"
                    elif agent_name in ["DataSpecialist", "AnalysisSpecialist"]:
                        current_role = "research"
                    elif agent_name == "NEOCommander":
                        current_role = "system"

                # Content Extraction
                if hasattr(event, "content") and event.content and hasattr(event.content, "parts"):
                    for p in event.content.parts:
                        if hasattr(p, "text") and p.text:
                            content_str += p.text
                        elif hasattr(p, "function_call") and p.function_call:
                            content_str += f"\n🚀 EXECUTING TOOL: {p.function_call.name}"
                        elif hasattr(p, "function_response") and p.function_response:
                            resp = p.function_response
                            if resp.name in ["fetch_neo_data_func", "calculate_asteroid_kinetic_energy"]:
                                yield f"data: {json.dumps({'type': 'telemetry', 'content': resp.response})}\n\n"
                                if resp.name == "fetch_neo_data_func":
                                    content_str += "\n📡 SENSOR DATA RECEIVED. ASSEMBLING THREAT TABLE..."
                                else:
                                    content_str += "\n⚡ KINETIC CALCULATIONS COMPLETE. THREAT LEVEL QUANTIFIED."
                            else:
                                content_str += f"\n✅ Tool {resp.name} completed."
                
                if content_str.strip():
                    # Record for Firestore
                    mission_trace_events.append({
                        "agent": agent_name or "Unknown",
                        "content": content_str.strip(),
                        "timestamp": datetime.datetime.utcnow().isoformat()
                    })
                    
                    yield f"data: {json.dumps({'type': 'log', 'content': content_str.strip(), 'role': current_role, 'server_time': get_ts()})}\n\n"
                    await asyncio.sleep(0.01)
            
            # [NEW] Persist full trace after success
            log_mission_trace(user_email, user_query, mission_trace_events)
            
        except Exception as e:
            error_msg = f"Agent Error: {str(e)}"
            yield f"data: {json.dumps({'type': 'log', 'content': f'⚠️ {error_msg}'})}\n\n"

    return StreamingResponse(event_generator(), headers=headers, media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
