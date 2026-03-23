import os
from datetime import datetime
from google.cloud import firestore

# Initialize Firestore client
# In Cloud Run, it will automatically use the project ID from the environment.
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "adk-beta-1")
db = firestore.Client(project=project_id)

def log_user_login(email: str, ip_address: str = "unknown"):
    """
    Records a user login event in the 'user_sessions' collection.
    """
    try:
        doc_ref = db.collection("user_sessions").document()
        doc_ref.set({
            "email": email,
            "login_time": datetime.utcnow(),
            "ip_address": ip_address,
            "platform": "NEO-Threat-Calculator"
        })
        print(f"Logged login for {email}")
    except Exception as e:
        print(f"Failed to log user login: {str(e)}")

def log_mission_trace(email: str, tactical_order: str, steps: list):
    """
    Records an agent reasoning trace in the 'mission_logs' collection.
    'steps' should be a list of reasoning strings or objects.
    """
    try:
        doc_ref = db.collection("mission_logs").document()
        doc_ref.set({
            "email": email,
            "tactical_order": tactical_order,
            "steps": steps,
            "timestamp": datetime.utcnow()
        })
        print(f"Logged mission trace for {email}")
    except Exception as e:
        print(f"Failed to log mission trace: {str(e)}")
