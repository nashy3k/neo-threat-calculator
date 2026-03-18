from authlib.integrations.starlette_client import OAuth
from fastapi import Request, HTTPException
from config.secrets import get_secret
import os

# Initialize OAuth
oauth = OAuth()

# Google OAuth Configuration
# We fetch Client ID and Secret from Secret Manager for production security
GOOGLE_CLIENT_ID = get_secret("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = get_secret("GOOGLE_CLIENT_SECRET")

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

def get_allowed_users():
    """Returns a list of email addresses allowed to access the dashboard."""
    # We fetch the allow-list from Secret Manager for production management.
    # Fallback to hardcoded default for initial setup.
    allowed = get_secret("ALLOWED_USERS")
    if not allowed:
        allowed = "nashy3k@gmail.com" # Default to user's known address
    return [email.strip() for email in allowed.split(",")]

async def verify_auth(request: Request):
    """Dependency to verify if a user is logged in via session."""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    email = user.get("email")
    if email not in get_allowed_users():
        raise HTTPException(status_code=403, detail="Forbidden: You are not in the allow-list.")
    
    return user
