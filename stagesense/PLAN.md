# StageSense — PLAN.md

> *The AI that sees what you can't.*
> NYC Build With AI Hackathon | Category: Live Agent

---

## Project Status

| Phase | What | Status |
|-------|------|--------|
| Phase 0 | Repo scaffold + dependencies | ✅ Complete |
| Phase 1 | Backend core (WebSocket + Gemini Live) | ✅ Complete (14 bugs fixed) |
| Phase 2 | Two agent modes + JSON output tuning | 🔜 Next |
| Phase 3 | SSE dashboard + mobile capture UI | ⬜ |
| Phase 4 | Audio whisper + Cloud Run deploy | ⬜ |

---

## Product Summary

**StageSense** is a live AI presentation coach built on Google ADK and Gemini Live API.

Two camera modes:

| Mode | Camera faces | AI analyzes | Output |
|------|-------------|-------------|--------|
| **Coach** | Speaker | Pace, clarity, energy, fillers | Live scorecard + whispered action |
| **Room Read** | Audience | Engagement, confusion, excitement | Alert whispers to speaker |

**Demo setup:**
- 📱 Phone (presenter): `index.html` — camera + mic → WebSocket → backend
- 💻 Laptop/projector: `dashboard.html` — SSE scorecard streaming live

---

## Phase 0 — Scaffold ✅

**Goal:** Project structure, git, dependencies installed.

**Architecture:**
```
stagesense/
├── backend/    ← FastAPI + venv (.venv) ← START HERE
└── frontend/   ← Static HTML, served from backend
```

**Completed:**
- `backend/main.py` — FastAPI skeleton with `/ws`, `/stream`, `/mode`, `/health`
- `backend/agent.py` — `StageSenseAgent` with Coach + RoomRead Gemini Live instructions
- `frontend/index.html` — mobile capture (getUserMedia + WebSocket sender)
- `frontend/dashboard.html` — SSE scorecard with animated bars + insight feed
- Git initialized, initial commit `7d85cb5`
- All packages installed and syntax verified

---

## Phase 1 — Backend Core ✅ Complete

**Goal:** End-to-end audio pipeline working: mobile mic → WebSocket → Gemini Live → SSE → dashboard.

**All fixes applied:**
- [x] Bug 1 — New `stagesense/Dockerfile` (frontend COPY within build context)
- [x] Bug 2 — StaticFiles mounted in `main.py` — serves `index.html` at `/`
- [x] Bug 3 — `active_session` guard prevents concurrent session collisions
- [x] Bug 4 — Switched to `gemini-2.0-flash-live-001` + `response_modalities=["TEXT"]`
- [x] Bug 5 — Robust `_parse_scores()` with first-brace JSON extraction
- [x] Bug 6 — `videoInterval` stored and cleared on session stop
- [x] Bug 7 — `AudioContext` closed on session stop (no more memory leak)
- [x] Bug 9 — SSE generator has `CancelledError` handler (L5 pattern)
- [x] Bug 10 — `--proxy-headers` added to Dockerfile CMD (wss:// on Cloud Run)
- [x] Bug 11 — StaticFiles mount confirmed last in `main.py`
- [x] Bug 13 — `run_session()` uses `asyncio.gather` + score queue (no deadlock)
- [x] Bug 14 — Initial stimulus sent to wake Gemini Live model immediately
- [x] Gap — Startup env validation (fail-fast on missing `GOOGLE_CLOUD_PROJECT`)

**Run command:**
```powershell
$env:GOOGLE_CLOUD_PROJECT = "ai-hack-489018"
$env:GOOGLE_GENAI_USE_VERTEXAI = "true"
$env:GOOGLE_CLOUD_LOCATION = "us-central1"
.venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

**Verification:**
- `GET /health` returns `{"status": "ok", "mode": "coach", "session_active": false}`
- Open `http://localhost:8080/` → shows mobile capture page ✅
- Open `http://localhost:8080/dashboard.html` → shows "Waiting for session"
- `curl -N http://localhost:8080/stream` → SSE events stream every 0.5s
- Open `index.html` → grant camera/mic → Start Session → scores appear on dashboard

---

## Phase 2 — Agent Modes 🔜 Next

**Goal:** Both Coach and Room Read modes produce meaningful, consistent JSON scores.

**Key tasks:**
- [ ] Coach mode: pace/clarity/energy scores update every ~5s
- [ ] Room Read mode: engagement/confusion/excitement update every ~3s
- [ ] Mode toggle (`POST /mode/roomread`) switches Gemini Live instruction
- [ ] `action`/`alert` strings are short and actionable (< 12 words)
- [ ] No JSON parse errors in logs

**Tuning the instructions:**
- If scores are always 0: check `response_modalities` includes `"TEXT"`
- If output is prose not JSON: strengthen system instruction — "OUTPUT ONLY JSON"
- If parse fails: log `part.text` raw, adjust `_parse_scores` regex

---

## Phase 3 — Dashboard + Mobile UI

**Goal:** Dashboard is beautiful, readable from a projector. Mobile page is thumb-friendly.

**Key tasks:**
- [ ] Dashboard auto-connects SSE on load and auto-reconnects on drop
- [ ] Score bars animate smoothly (CSS transition already set to 0.8s)
- [ ] Mode badge switches Coach ↔ Room Read with correct color
- [ ] Mobile: camera preview shows speaker (front cam in Coach, rear in Room Read)
- [ ] Mobile: "whisper" text appears below video when AI sends coaching
- [ ] Serve `frontend/` as static files from FastAPI
  ```python
  from fastapi.staticfiles import StaticFiles
  app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
  ```

---

## Phase 4 — Polish + Deploy

**Goal:** Deployed on Cloud Run with HTTPS (required for mobile camera).

**Key tasks:**
- [ ] Test on real phone over HTTPS
- [ ] Deploy from `stagesense/` root (not `backend/`) — Dockerfile now at root
- [ ] Verify SSE works through Cloud Run
- [ ] Demo rehearsal: 5 full run-throughs with real phone

**Deploy from `stagesense/` root:**
```bash
gcloud run deploy stagesense \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --timeout 3600 \
  --memory 1Gi \
  --set-env-vars GOOGLE_CLOUD_PROJECT=ai-hack-489018,GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_LOCATION=us-central1
```

---

## Judging Alignment

| Criterion | How StageSense Delivers |
|-----------|------------------------|
| **Innovation & UX** | Live audio coaching whisper + live audience reads — no text box at all |
| **Technical** | Gemini Live API, ADK agents, FastAPI, SSE, Cloud Run, noise suppression |
| **Demo & Story** | "This AI coached us through this very demo" — demo IS the product |

---

## Known Risks + Mitigations

| Risk | Mitigation |
|------|-----------|
| Gemini Live auth failure | Use `GOOGLE_GENAI_USE_VERTEXAI=true` + `gcloud auth application-default login` |
| Mobile camera blocked (HTTPS) | Must deploy to Cloud Run before phone demo |
| iOS AudioContext suspended | Resume on button tap event |
| Room noise bleeds into coaching | `noiseSuppression: true` already set; use earbuds for cleaner mic |
| SSE drops on Cloud Run after 60s | `--timeout 3600` flag on deploy |
| Gemini outputs prose instead of JSON | Reinforce instruction: "Output ONLY valid JSON. No other text." |

---

## Tech Stack Reference

| Component | Technology | Source Pattern |
|-----------|-----------|---------------|
| Live audio/video AI | Gemini Live API (`gemini-live-2.5-flash-preview-native-audio`) | Way Back Home L3 |
| Streaming backend | FastAPI + WebSocket + SSE | Way Back Home L3 + L5 |
| Agent orchestration | Google ADK | Way Back Home L1–L5 |
| Frontend | Vanilla HTML/CSS/JS | Way Back Home L5 dashboard |
| Hosting | Cloud Run | Way Back Home all levels |
| Auth | Vertex AI + ADC | Way Back Home all levels |
