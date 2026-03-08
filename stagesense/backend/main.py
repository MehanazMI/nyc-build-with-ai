"""
StageSense Backend — main.py
FastAPI server with:
- /ws  WebSocket: receives audio+video frames from mobile browser
- /stream SSE: streams live scores to dashboard
- /mode  toggle Coach/RoomRead mode
- /health health check
"""
import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from agent import StageSenseAgent

load_dotenv()
logging.basicConfig(level=logging.INFO)
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_instance
    agent_instance = StageSenseAgent()
    logger.info("StageSense agent initialized")
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
    return {"status": "ok", "mode": current_mode}


# ─── SSE Dashboard Stream (from Level 5 pattern) ─────────────────────────────

@app.get("/stream")
async def stream(request: Request):
    async def generator():
        while True:
            if await request.is_disconnected():
                break
            yield {
                "event": "score_update",
                "data": json.dumps(latest_scores),
            }
            await asyncio.sleep(0.5)
    return EventSourceResponse(generator())


# ─── WebSocket — Audio/Video Receiver ────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Mobile client connected")

    try:
        # Start Gemini Live session based on current mode
        async for scores in agent_instance.run_session(websocket, lambda: current_mode):
            # Update global state for SSE streaming
            latest_scores.update(scores)
            latest_scores["mode"] = current_mode

            # Send audio coaching whisper back to mobile (TTS)
            action = scores.get("action") or scores.get("alert", "")
            if action:
                await websocket.send_text(json.dumps({
                    "type": "whisper",
                    "text": action,
                }))

    except WebSocketDisconnect:
        logger.info("Mobile client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()
