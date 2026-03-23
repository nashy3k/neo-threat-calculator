import os
from google.cloud import secretmanager

def get_secret(secret_id: str, project_id: str = None) -> str:
    """
    Retrieves a secret from GCP Secret Manager.
    If the secret is not found or in a local environment without GCP access,
    it falls back to os.getenv (for local dev compatibility).
    """
    # 1. Fallback to Environment Variable first (to avoid latency in local dev)
    env_val = os.getenv(secret_id)
    if env_val:
        return env_val

    # 2. Attempt Secret Manager
    if not project_id:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "adk-beta-1")

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"WARNING: Could not fetch secret {secret_id} from Secret Manager: {str(e)}")
        # Final fallback to DEMO values if it's the NASA key or Session key
        if secret_id == "NASA_API_KEY":
            return "DEMO_KEY"
        if secret_id == "SESSION_SECRET_KEY":
            return "temporary-dev-session-key-2026"
        return ""
