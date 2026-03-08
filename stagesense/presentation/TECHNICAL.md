# StageSense — Technical Details

> For judges, reviewers, or curious engineers.

---

## Architecture Overview

```
📱 Phone (camera + mic)
        │
        │  WebSocket — raw audio (PCM 16kHz) + video (JPEG frames)
        ▼
┌─────────────────────────────────────────┐
│  FastAPI Backend (Cloud Run)            │
│  ├── /ws      WebSocket endpoint        │
│  ├── /stream  SSE dashboard feed        │
│  └── /mode    coach | roomread toggle   │
│                                         │
│  Google ADK Runner                      │
│  └── LiveRequestQueue                   │
└─────────────────────────────────────────┘
        │
        │  Bidirectional audio stream (v1alpha)
        ▼
┌─────────────────────────────────────────┐
│  Gemini Live API                        │
│  gemini-live-2.5-flash-preview          │
│  -native-audio-09-2025                  │
│                                         │
│  Analyzes: voice tone, pace, clarity,   │
│  filler words, energy, facial cues      │
└─────────────────────────────────────────┘
        │
        │  JSON scorecard (every ~5s)
        ▼
  FastAPI → SSE push → 💻 Dashboard
```

---

## Key Technical Decisions

### 1. Gemini Live API — Native Audio Model
- Uses **bidirectional WebSocket** (`bidiGenerateContent`) — not REST, not polling
- Model sees continuous audio stream, responds with coaching in real time
- `output_audio_transcription` captures model text output as scores
- SDK version: `google-genai==1.56.0` (v1alpha endpoint — required for native audio)

### 2. Google ADK Runner + LiveRequestQueue
- `Runner.run_live()` manages session lifecycle, reconnection, and event routing
- `LiveRequestQueue` decouples audio ingestion from model response — no deadlock
- Two agents: `stagesense_coach` and `stagesense_roomread`
- `asyncio.gather(upstream, downstream)` — concurrent bidirectional streaming

### 3. FastAPI — WebSocket + SSE
- `/ws` — ingest raw PCM audio and JPEG video frames from mobile
- `/stream` — Server-Sent Events push scores to dashboard (no polling)
- Session guard prevents concurrent connections colliding on shared state
- `load_dotenv(override=True)` — prevents shell env var leaks from corrupting auth

### 4. Frontend — Vanilla HTML/CSS/JS
- `getUserMedia()` — browser captures mic + camera with no native app required
- `AudioContext` + `ScriptProcessorNode` — converts browser audio to PCM 16kHz
- `EventSource` API — dashboard subscribes to SSE, auto-reconnects on drop
- Web Speech API — speaks whispered coaching tips aloud to presenter

---

## Agent Instructions

### Coach Mode
Analyzes speaker delivery every 5 seconds.  
Outputs JSON: `{pace, clarity, energy, filler_count, insight, action}`

### Room Read Mode
Analyzes audience engagement every 3 seconds.  
Outputs JSON: `{engagement, confusion, excitement, alert}`

Both agents instructed to output **only raw JSON** — no prose, no markdown.

---

## Resilience

- **Simulation fallback** — if Gemini Live fails to connect, realistic scores are generated automatically so the demo always runs
- **CancelledError handler** on SSE generator — clean shutdown on client disconnect
- **Session guard** — rejects second concurrent WebSocket to prevent score collisions
- **Pydantic warnings suppressed** — ADK serialization warnings silenced for clean logs

---

## Stack Summary

| Layer | Technology | Version |
|-------|-----------|---------|
| AI model | Gemini Live API | native audio (v1alpha) |
| Agent framework | Google ADK | 1.24.1 |
| SDK | google-genai | 1.56.0 |
| Backend | FastAPI + uvicorn | 0.128+ |
| Hosting | Google Cloud Run | — |
| Auth | Vertex AI + ADC | — |
| Frontend | Vanilla HTML/CSS/JS | — |
