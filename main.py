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

@app.get("/stream-assessment")
async def stream_assessment(user_query: str = "Identify major NEO threats"):
    """
    Streams the LoopAgent's reasoning steps and tool outputs as SSE.
    """
    async def event_generator():
        # Setup session for streaming
        from google.adk.runners import InMemoryRunner
        runner = InMemoryRunner(commander_agent)
        
        # Explicit model config for Vertex AI robustness as per global rules
        async with runner.stream_async(
            user_query, 
            app_id="NEOThreatCalculator",
            session_id="neo_live_stream"
        ) as stream:
            async for event in stream:
                # Yield only the parts that are valuable for the UI
                # We can refine this to send specific event types (thought, action, observation)
                data = {
                    "type": event.event_type.name if hasattr(event, 'event_type') else "log",
                    "content": str(event)
                }
                yield f"data: {json.dumps(data)}\n\n"
                await asyncio.sleep(0.1) # Smooth streaming

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "Check threats")
    from google.adk.runners import InMemoryRunner
    runner = InMemoryRunner(commander_agent)
    response = await runner.run(message, app_id="NEOThreatCalculator", session_id="neo_chat")
    return {"response": response.text}

if __name__ == "__main__":
    import uvicorn
    # Use 8080 as standard for Cloud Run
    uvicorn.run(app, host="0.0.0.0", port=8080)
