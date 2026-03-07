# Level 3 — Process SOS Signals (Biometric Scanner)

## Overview

Level 3 builds a **real-time biometric scanner** using the **Gemini Live API** and **ADK's bidirectional streaming**. The agent watches a live camera feed, detects hand gestures (finger count), and reports them via a `report_digit` tool — all over WebSocket.

**Key difference from L1/L2:** This is a **live streaming agent**, not a request-response agent. Audio/video flows continuously via WebSocket ↔ Gemini Live API.

## Architecture

```
Browser (camera + mic) ──WebSocket──► FastAPI (port 8080)
                                         ├── upstream_task: WS → LiveRequestQueue
                                         ├── downstream_task: runner.run_live() → WS
                                         └── biometric_agent (ADK Agent)
                                              ├── model: gemini-live-2.5-flash-preview-native-audio
                                              ├── tool: report_digit(count)
                                              └── instruction: detect fingers, call tool, confirm
```

## Files to Modify

| File | Markers | Lines (starter → solution) |
|------|---------|---------------------------|
| `backend/app/biometric_agent/agent.py` | 4 (`REPLACE TOOLS`, `REPLACE_MODEL`, `TOOL CONFIG`, `REPLACE INSTRUCTIONS`) | 21 → 53 |
| `backend/app/main.py` | 4 (`REPLACE_RUNNER_CONFIG`, `REPLACE_SESSION_INIT`, `REPLACE_LIVE_REQUEST`, `REPLACE_SORT_RESPONSE`) | 109 → 277 |

**Frontend:** Identical between starter and solution — no changes needed.

## Detailed Changes

### `biometric_agent/agent.py`

#### `#REPLACE TOOLS` (line 9)
```python
def report_digit(count: int):
    """
    CRITICAL: Execute this tool IMMEDIATELY when a number of fingers is detected.
    Sends the detected finger count (1-5) to the biometric security system.
    """
    print(f"\n[SERVER-SIDE TOOL EXECUTION] DIGIT DETECTED: {count}\n")
    return {"status": "success", "digit": count}
```

#### `#REPLACE_MODEL` (line 11)
```python
MODEL_ID = os.getenv("MODEL_ID", "gemini-live-2.5-flash-preview-native-audio-09-2025")
```

#### `#TOOL CONFIG,` (line 16)
```python
tools=[report_digit],
```

#### `#REPLACE INSTRUCTIONS` (line 18)
Full biometric scanner instruction — wait for trigger, count fingers, call `report_digit`, confirm verbally, stay robotic and brief.

---

### `backend/app/main.py`

#### `#REPLACE_RUNNER_CONFIG` (line 64)
```python
session_service = InMemorySessionService()
runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)
```

#### `#REPLACE_SESSION_INIT` (line 91)
Auto-detect model type (native-audio vs half-cascade), configure `RunConfig` with appropriate modalities, proactivity, transcription. Create/get session.

#### `#REPLACE_LIVE_REQUEST` (line 93)
Create `LiveRequestQueue`, send initial "Hello" stimulus, define `upstream_task()` (WS → queue: handles binary audio, JSON text, JSON audio, JSON image).

#### `#REPLACE_SORT_RESPONSE` (line 95)
Define `downstream_task()` (Gemini → WS: logs tool calls, transcriptions), `asyncio.gather(upstream, downstream)`, WebSocket disconnect handling, queue cleanup.

## Infrastructure

**None required.** No databases, no new APIs, no GCS. Just env vars:

```env
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=ai-hack-489018
GOOGLE_CLOUD_LOCATION=us-central1
MODEL_ID=gemini-live-2.5-flash-preview-native-audio-09-2025
```

## Execution Order

1. Create `backend/app/.env`
2. Fill 4 markers in `agent.py`
3. Fill 4 markers in `main.py`
4. `uv sync` to install deps
5. Build frontend: `npm install && npm run build`
6. Run: `uv run python -m backend.app.main` (port 8080)

## Verification

- Backend starts on `:8080` without import errors
- WebSocket connects at `/ws/user1/test-session`
- Agent responds with "Biometric Scanner Online. Awaiting neural handshake."
- Showing fingers to camera → `report_digit` tool call appears in server logs

## Review Audit Table

| Pass | Items Found | Details |
|------|-------------|---------|
| 1 — Scope | 7 markers, 2 files, no frontend changes, no infra | Architecture: WebSocket ↔ Gemini Live API |
| 2 — Deep Scan | Confirmed 7+1 markers (TOOL CONFIG comma), model ID from env, mock server available | Frontend identical to solution |
| 3 — Full Diff | *pending* | |
