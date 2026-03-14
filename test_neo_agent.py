import asyncio
import os
from agent.commander import commander_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

async def test_agent():
    print("🚀 Starting NEO Threat Assessment Test...")
    prompt = "Find the most dangerous asteroid approaching Earth in the next 7 days and calculate its kinetic energy."
    
    app_name = "NEOThreatCalculator"
    user_id = "test_user"
    session_id = "test_session"

    # Create the runner with the matching app_name
    runner = InMemoryRunner(agent=commander_agent, app_name=app_name)
    
    print(f"\nInitializing session: {session_id} in app: {app_name}...")
    # Initialize the session
    await runner.session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    new_message = types.Content(parts=[types.Part(text=prompt)])
    
    print(f"\nUser: {prompt}")
    print("-" * 20)
    
    try:
        # runner.run is a sync generator that yields events
        # It handles the async runner.run_async internally on a separate thread.
        for event in runner.run(
            user_id=user_id, 
            session_id=session_id, 
            new_message=new_message
        ):
            if hasattr(event, 'content') and event.content:
                 print(f"\nFinal Answer: {event.content}")
            elif hasattr(event, 'agent_id'):
                 print(f"[{event.agent_id}] Thinking...")
            else:
                 # Print the event type for visibility in case of other events
                 # Use print_event if available in ADK for better formatting
                 pass
    except Exception as e:
        print(f"❌ Error during execution: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent())
