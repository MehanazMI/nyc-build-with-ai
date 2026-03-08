# AGENTS.md

> Guidance for AI coding agents working on **StageSense**.
> *The AI that sees what you can't.*
> Project: `ai-hack-489018` | Event: NYC Build With AI Hackathon

---

## ⚠️ Critical: File Layout

```
stagesense/
├── backend/
│   ├── main.py      ← FastAPI app — WebSocket + SSE + mode toggle
│   ├── agent.py     ← Gemini Live sessions (Coach + RoomRead)
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/
    ├── index.html   ← 📱 Mobile: camera + mic capture + WebSocket sender
    └── dashboard.html ← 💻 Projector: SSE scorecard
```

**Never edit `frontend/` files in the backend context.** They are served as static files.

---

## Setup

```powershell
cd stagesense/backend
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

# Environment
$env:GOOGLE_CLOUD_PROJECT = "ai-hack-489018"
$env:GOOGLE_GENAI_USE_VERTEXAI = "true"
$env:GOOGLE_CLOUD_LOCATION = "us-central1"

# Run
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

**Open in browser:**
- Mobile capture: `http://localhost:8080/` (or open `frontend/index.html` directly)
- Dashboard: `http://localhost:8080/dashboard` (or `frontend/dashboard.html`)

---

## Architecture

```
📱 Mobile Browser (camera + mic)
        │
        │ WebSocket /ws (binary: PCM audio + JPEG video frames)
        ▼
FastAPI Backend (:8080)
  ├── /ws   → receives frames → StageSenseAgent.run_session()
  │                               ↓
  │                          Gemini Live session
  │                          (Coach OR RoomRead instruction)
  │                               ↓
  │                          parsed JSON scores
  │                               ↓
  ├── latest_scores dict ←── updated every 3–5 seconds
  │
  ├── /stream → SSE → 💻 Dashboard (score_update events)
  ├── /mode  → toggle Coach ↔ RoomRead
  └── /health → health check

💻 Dashboard Browser
  └── EventSource /stream → animates score bars + insight feed
```

---

## Two Agent Modes

### Coach Mode — watches the SPEAKER
Agent instruction tells Gemini Live to analyze:
- **Pace** (0–100): speaking speed relative to ideal
- **Clarity** (0–100): articulation and word choice
- **Energy** (0–100): vocal confidence and presence
- **Filler count**: "um", "uh", "like", "you know" in last 30s
- **Insight**: one concrete observation
- **Action**: one immediate spoken coaching whisper

### Room Read Mode — watches the AUDIENCE
Flip camera at the crowd. Agent analyzes faces and body language:
- **Engagement** (0–100): attention and focus
- **Confusion** (0–100): lost expressions, furrowed brows
- **Excitement** (0–100): leaning in, nodding, smiling
- **Alert**: one actionable whisper ("Row 2 losing interest — add an example")

---

## Key Patterns (inherited from Way Back Home)

### Gemini Live Session (from L3)
```python
from google import genai
from google.genai import types as genai_types

client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)

async with client.aio.live.connect(model=MODEL, config=config) as session:
    # upstream: send audio/video frames
    await session.send_realtime_input(media=blob)
    # downstream: receive model output
    async for response in session.receive():
        ...
```

### WebSocket Audio Streaming (from L3)
```python
@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    async for scores in agent.run_session(websocket, lambda: current_mode):
        latest_scores.update(scores)
```

### SSE Score Stream (from L5)
```python
@app.get("/stream")
async def stream(request: Request):
    async def gen():
        while True:
            if await request.is_disconnected(): break
            yield {"event": "score_update", "data": json.dumps(latest_scores)}
            await asyncio.sleep(0.5)
    return EventSourceResponse(gen())
```

### Video Frame Sending (mobile browser)
```javascript
// Audio: PCM Int16Array sent as binary
const int16 = new Int16Array(floatBuffer.length);
ws.send(int16.buffer);

// Video: JPEG blob prefixed with "VID:"
canvas.toBlob(blob => {
    const prefix = new TextEncoder().encode('VID:');
    // combine prefix + jpeg bytes → send as binary
    ws.send(combined.buffer);
}, 'image/jpeg', 0.7);
```

### Frame Type Detection (backend)
```python
if data[:4] == b"VID:":
    blob = genai_types.Blob(data=data[4:], mime_type="image/jpeg")
else:
    blob = genai_types.Blob(data=data, mime_type="audio/pcm;rate=16000")
await session.send_realtime_input(media=blob)
```

---

## Common Gotchas

| Gotcha | Fix |
|--------|-----|
| `getUserMedia` fails silently | HTTPS required in production; localhost is exempt |
| Mobile mic picks up room noise | Enable `noiseSuppression: true` in getUserMedia constraints |
| Camera facing mode unsupported | Catch exception, fall back to `{video: true}` without facingMode |
| SSE drops after 60s (Cloud Run) | Set `--timeout 3600` on Cloud Run service |
| Gemini Live gives no text output | Ensure `response_modalities` includes `"TEXT"` in config |
| JSON parse fails on partial output | Only parse lines starting with `{` — skip narration text |
| AudioContext suspended on iOS | Resume on first user gesture: `audioContext.resume()` |
| `VID:` prefix not detected | Check `data[:4]` is bytes, not string — use `websocket.receive_bytes()` |
| Mode switches mid-session | Restart Gemini Live session on mode change for cleaner output |
| Upstream task not cancelled | Always `upstream_task.cancel()` in `finally` block |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `WebSocket` | `/ws` | Receive audio+video from mobile |
| `GET` | `/stream` | SSE score stream to dashboard |
| `POST` | `/mode/{mode}` | Switch `coach` or `roomread` |
| `GET` | `/mode` | Current mode |
| `GET` | `/health` | Health check |

---

## JSON Score Schemas

**Coach Mode output** (every ~5 seconds):
```json
{
  "pace": 78,
  "clarity": 65,
  "energy": 89,
  "filler_count": 3,
  "insight": "Good energy — speaking too fast on technical terms",
  "action": "Slow down — breathe"
}
```

**Room Read Mode output** (every ~3 seconds):
```json
{
  "engagement": 72,
  "confusion": 41,
  "excitement": 55,
  "alert": "Row 2 losing attention — give a concrete example now"
}
```

---

## GCP Resources

| Resource | Value |
|----------|-------|
| Project | `ai-hack-489018` |
| Region | `us-central1` |
| Model | `gemini-live-2.5-flash-preview-native-audio` |
| Cloud Run service | `stagesense` |
| Service Account | `way-back-home-sa@ai-hack-489018.iam.gserviceaccount.com` |

---

## Deploy to Cloud Run

```bash
gcloud run deploy stagesense \
  --source backend/ \
  --region us-central1 \
  --allow-unauthenticated \
  --timeout 3600 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=ai-hack-489018,GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_LOCATION=us-central1
```

---

## Demo Script

```
1. Open dashboard.html on projector/laptop
2. Open index.html on phone
3. Select COACH MODE → press Start Session
4. Present for 60 seconds → watch dashboard fill with live scores
5. Say "Let's read the room" → tap ROOM READ → flip phone at audience
6. AI reads judges' reactions live → alerts appear on dashboard
7. "This AI coached us through this very demo."
```

---

## Reference

- [PLAN.md](PLAN.md) — Build phase tracker
- [ADK Docs](https://google.github.io/adk-docs/)
- [Gemini Live API](https://ai.google.dev/api/live)
- [Way Back Home L3 pattern](../way-back-home/level_3/) — WebSocket + Gemini Live reference
- [Way Back Home L5 pattern](../way-back-home/level_5/) — SSE streaming reference
