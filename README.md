# NEO Threat Calculator 🛰️

A premium "Control Room" dashboard for tracking Near Earth Objects (NEOs), calculating their kinetic energy, and assessing potential threats using Google's Agent Development Kit (ADK) and NASA's NeoWs API.

## 🚀 Features
- **Autonomous Reasoning**: Powered by Gemini 3 Flash via ADK.
- **Real-time Streaming**: Reasoning logs are streamed using Server-Sent Events (SSE).
- **Premium UI**: Custom "Control Room" dashboard with neural grid aesthetics.
- **NASA Integration**: Live data from the NeoWs (Near Earth Object Web Service) API.

## 📁 Project Structure
- `/agents` - Logic and prompts for the NEO Commander and Specialists.
- `/tools` - Custom tools for NASA API interaction and Python execution.
- `/app` - Web-based "Control Room" frontend.
- `main.py` - FastAPI server and SSE streaming logic.
- `Dockerfile` - Container config for Cloud Run.

## 🛠️ Local Development
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set your Google Cloud Project: `gcloud config set project [YOUR_PROJECT_ID]`.
4. Run the app: `uvicorn main:app --reload`.
5. Open `http://localhost:8080/static/index.html`.

## ☁️ Deployment
Deployed to Google Cloud Run using:
`gcloud run deploy neo-threat-calculator --source . --project [PROJECT_ID]`
