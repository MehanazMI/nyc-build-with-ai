# StageSense 🎤

> *The AI that sees what you can't.*

An AI-powered live presentation coach with two modes:
- **Coach Mode** — camera faces the speaker → real-time coaching on pace, clarity, energy, filler words
- **Room Read Mode** — camera faces the audience → AI reads engagement, confusion, excitement

Built with Google ADK, Gemini Live API, FastAPI, SSE — on Google Cloud.

## Team

**The Sixth Sense**

- Mehanaz MI
- Abdul Rasheed

## Setup

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# Set env vars
export GOOGLE_CLOUD_PROJECT=ai-hack-489018
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_LOCATION=us-central1

# Run
uvicorn main:app --host 0.0.0.0 --port 8080
```

Open `frontend/index.html` on your phone, `frontend/dashboard.html` on the projector.

## Architecture

```
📱 Mobile (camera+mic) → WebSocket → FastAPI → Gemini Live
                                         ↓
                                    ADK Agent
                                         ↓
                                    SSE stream → 💻 Dashboard
```

## Tech Stack

- **Google ADK** — CoachAgent + RoomReadAgent
- **Gemini Live API** — real-time audio+video analysis
- **FastAPI + WebSocket** — audio/video ingestion
- **SSE** — live scorecard streaming to dashboard
- **Cloud Run** — hosting
