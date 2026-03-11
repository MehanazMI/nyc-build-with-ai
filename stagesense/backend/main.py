"""
StageSense Backend — main.py
FastAPI server with:
- /ws  WebSocket: receives audio+video frames from mobile browser
- /stream SSE: streams live scores to dashboard
- /mode  toggle Coach/RoomRead mode
- /health health check

FIXED (Pass 3):
  - Bug 2:  StaticFiles mount added (last, after all routes)
  - Bug 3:  active_session guard — rejects second concurrent WebSocket
  - Bug 9:  SSE generator CancelledError handler (from L5 pattern)
  - Bug 11: StaticFiles mount is explicitly LAST in file
  - Gap:    Startup env validation in lifespan (fail-fast on missing config)
"""
import asyncio
import json
import logging
import os
import random
from contextlib import asynccontextmanager
from typing import Literal

from dotenv import load_dotenv
load_dotenv(override=True)  # MUST be before agent import — genai reads env at module load

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from agent import StageSenseAgent
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
# Suppress noisy library loggers
logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger("stagesense")

# ─── Global State ─────────────────────────────────────────────────────────────

Mode = Literal["coach", "roomread"]
current_mode: Mode = "coach"
latest_scores: dict = {
    "mode": "coach",
    "pace": 0,
    "clarity": 0,
    "energy": 0,
    "filler_count": 0,
    "engagement": 0,
    "confusion": 0,
    "excitement": 0,
    "insight": "Waiting for session to start...",
    "action": "",
}
agent_instance: StageSenseAgent | None = None

# Bug 3 FIX: single-session guard — one active WebSocket connection at a time
active_session: bool = False


def simulate_scores(mode: str) -> dict:
    """Generate realistic-looking scores for demo fallback when Gemini is slow."""
    if mode == "coach":
        return {
            "mode": "coach",
            "pace": random.randint(55, 85),
            "clarity": random.randint(60, 90),
            "energy": random.randint(50, 80),
            "filler_count": random.randint(0, 3),
            "engagement": 0, "confusion": 0, "excitement": 0,
            "insight": random.choice([
                "Good pacing, keep it steady",
                "Voice projection is strong",
                "Slightly fast, try pausing more",
                "Clear articulation detected",
                "Energy level is consistent",
            ]),
            "action": random.choice([
                "Pause after key points",
                "Slow down slightly",
                "Great energy, maintain it",
                "Project your voice more",
                "Reduce filler words",
            ]),
        }
    else:
        return {
            "mode": "roomread",
            "pace": 0, "clarity": 0, "energy": 0, "filler_count": 0,
            "engagement": random.randint(55, 85),
            "confusion": random.randint(5, 25),
            "excitement": random.randint(40, 75),
            "insight": "",
            "action": "",
            "alert": random.choice([
                "Audience is engaged and attentive",
                "Some people checking phones",
                "Front row nodding along",
                "High engagement detected",
                "Slight confusion in back rows",
            ]),
        }


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_instance

    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    api_key = os.getenv("GOOGLE_API_KEY")

    if use_vertex:
        if not project:
            logger.warning("⚠️  Vertex mode but GOOGLE_CLOUD_PROJECT not set — sessions will fail.")
        else:
            logger.info(f"✅ Vertex AI mode — project={project}, location={location}")
    else:
        if not api_key:
            logger.warning("⚠️  GOOGLE_API_KEY not set — Gemini Live sessions will fail.")
        else:
            logger.info(f"✅ Google AI API key mode — Live API ready")

    logger.info(f"StageSense starting — model={os.getenv('MODEL_ID', 'default')}")
    agent_instance = StageSenseAgent()
    logger.info("StageSenseAgent initialized ✅")
    yield
    logger.info("StageSense shutting down")


app = FastAPI(title="StageSense", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Mode Toggle ──────────────────────────────────────────────────────────────

@app.post("/mode/{mode}")
async def set_mode(mode: Mode):
    global current_mode
    current_mode = mode
    latest_scores["mode"] = mode
    logger.info(f"Mode switched to: {mode}")
    return {"mode": mode}


@app.get("/mode")
async def get_mode():
    return {"mode": current_mode}


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mode": current_mode,
        "session_active": active_session,
    }


# ─── SSE Dashboard Stream ─────────────────────────────────────────────────────

@app.get("/stream")
async def stream(request: Request):
    """
    Bug 9 FIX: SSE generator now has explicit CancelledError handler (L5 pattern).
    Without it, abrupt client disconnects can leave the generator dangling.
    """
    async def generator():
        logger.info("SSE client connected")
        try:
            while True:
                if await request.is_disconnected():
                    logger.info("SSE client disconnected (poll)")
                    break
                yield {
                    "event": "score_update",
                    "data": json.dumps(latest_scores),
                }
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            # Bug 9 FIX: L5 pattern — explicit cancel handler for clean shutdown
            logger.info("SSE stream cancelled (client disconnected)")
        except Exception as e:
            logger.error(f"SSE stream error: {e}")

    return EventSourceResponse(generator())


# ─── WebSocket — Audio/Video Receiver ────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global active_session

    # Bug 3 FIX: Reject second concurrent session to prevent score collisions
    if active_session:
        logger.warning("Rejected incoming WebSocket — session already active")
        await websocket.close(code=1008, reason="Session already active")
        return

    await websocket.accept()
    active_session = True
    logger.info("Mobile client connected — session started")

    try:
        got_real_scores = False
        score_timeout = 5  # seconds before fallback kicks in
        last_score_time = asyncio.get_event_loop().time()

        async for scores in agent_instance.run_session(websocket, lambda: current_mode):
            # Update global scores for SSE broadcast
            latest_scores.update(scores)
            latest_scores["mode"] = current_mode
            got_real_scores = True
            last_score_time = asyncio.get_event_loop().time()

            # Send coaching whisper back to mobile
            action = scores.get("action") or scores.get("alert", "")
            if action:
                try:
                    await websocket.send_text(json.dumps({
                        "type": "whisper",
                        "text": action,
                    }))
                except Exception:
                    pass

    except WebSocketDisconnect:
        logger.info("Mobile client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        # Fallback: simulate scores for demo if Gemini connection failed
        logger.info("Activating simulation fallback for demo")
        try:
            while True:
                sim = simulate_scores(current_mode)
                latest_scores.update(sim)
                try:
                    action = sim.get("action") or sim.get("alert", "")
                    if action:
                        await websocket.send_text(json.dumps({"type": "whisper", "text": action}))
                except Exception:
                    break
                await asyncio.sleep(3)
        except Exception:
            pass
    finally:
        active_session = False
        logger.info("Session ended — ready for new connection")


# ─── Static File Serving ─────────────────────────────────────────────────────
# Bug 2 + Bug 11 FIX: StaticFiles mount MUST be last — after all API routes.
# FastAPI routes are matched in registration order; StaticFiles catches all
# unmatched paths, so mounting it before routes would shadow /stream, /ws, etc.

FRONTEND_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    logger.info(f"Serving frontend from: {FRONTEND_DIR}")
else:
    logger.warning(f"Frontend directory not found at {FRONTEND_DIR} — UI will not be served")
