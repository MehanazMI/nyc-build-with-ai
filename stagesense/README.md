# StageSense 🎤

> *The AI that sees what you can't.*
> **NYC Build With AI Hackathon — Team: The Sixth Sense**

---

## What It Does

StageSense is a **live AI presentation coach** powered by Gemini Live API and Google ADK.

Point your phone at the **speaker** → get real-time coaching on pace, clarity, energy, and filler words.  
Point your phone at the **audience** → get live engagement, confusion, and excitement readings.

No text boxes. No uploads. Just camera + mic → AI → live dashboard.

---

## Team

**The Sixth Sense**

- Mehanaz MI
- Abdul Rasheed

---

## Demo Setup

**Requirements:** Python 3.11+, Google Cloud project with ADC configured

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Configure (Windows)
$env:GOOGLE_CLOUD_PROJECT = "ai-hack-489018"
$env:GOOGLE_GENAI_USE_VERTEXAI = "true"
$env:GOOGLE_CLOUD_LOCATION = "us-central1"

# Run
uvicorn main:app --host 0.0.0.0 --port 8080
```

| URL | Purpose |
|-----|---------|
| `http://localhost:8080/` | 📱 Mobile capture page (start session here) |
| `http://localhost:8080/dashboard.html` | 💻 Live scorecard dashboard |

---

## Architecture

```
📱 Phone (camera + mic)
        │
        │  WebSocket (audio/video frames)
        ▼
┌─────────────────────────────────────┐
│  FastAPI Backend                    │
│  ├── /ws  ← WebSocket endpoint      │
│  ├── /stream ← SSE dashboard feed   │
│  └── /mode  ← coach / roomread      │
│                                     │
│  Google ADK Runner                  │
│  └── LiveRequestQueue               │
│        │                            │
│        ▼                            │
│  Gemini Live API (native audio)     │
│  gemini-live-2.5-flash-preview      │
└─────────────────────────────────────┘
        │
        │  SSE (score JSON every 0.5s)
        ▼
💻 Dashboard (live animated scorecard)
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Live AI | Gemini Live API — `gemini-live-2.5-flash-preview-native-audio` |
| Agent framework | Google ADK — Runner + LiveRequestQueue |
| Backend | FastAPI + WebSocket + SSE (Server-Sent Events) |
| Frontend | Vanilla HTML/CSS/JS — no framework |
| Hosting | Google Cloud Run |
| Auth | Vertex AI + Application Default Credentials |
