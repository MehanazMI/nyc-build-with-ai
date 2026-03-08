"""
StageSense Agent — agent.py

Exact Way Back Home L3 pattern with google-genai==1.56.0 + google-adk==1.24.1:
- ADK Runner + InMemorySessionService + LiveRequestQueue
- Model: gemini-live-2.5-flash-preview-native-audio-09-2025 (v1alpha, Vertex)
- AUDIO modality + output_audio_transcription to capture JSON text
- upstream: websocket.receive() dict (handles bytes + disconnect cleanly)
- downstream: JSON captured from final_transcript and text parts
- asyncio.gather(upstream, downstream) — prevents deadlock on disconnect
- Hello stimulus sent AFTER first event (runner is connected before sending)
"""
import asyncio
import json
import logging
import os
import warnings
from typing import AsyncIterator, Callable

from google.adk.agents import Agent
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

load_dotenv(override=True)

# Suppress pydantic serialization warnings from ADK (L3 pattern)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

logger = logging.getLogger("stagesense.agent")

APP_NAME = "stagesense"
MODEL_ID = os.getenv("MODEL_ID", "gemini-live-2.5-flash-preview-native-audio-09-2025")

COACH_INSTRUCTION = """
You are StageSense Coach — a real-time live presentation coach.
You receive continuous audio and video of a presenter speaking on stage.

YOUR ONLY JOB: Every 5 seconds, output a JSON scorecard and nothing else.

OUTPUT FORMAT — speak exactly this JSON, nothing before or after:
{"pace": <0-100>, "clarity": <0-100>, "energy": <0-100>, "filler_count": <integer>, "insight": "<12 words max>", "action": "<12 words max>"}

SCORING:
- pace: 0=too fast or silent, 50=too slow, 100=ideal conversational pace
- clarity: 100=crisp articulation and clear vocabulary
- energy: 100=confident, projected, engaged voice
- filler_count: "um", "uh", "like", "you know" in last 30 seconds
- insight: one specific thing you observe about delivery
- action: one immediate coaching tip (e.g. "Slow down", "Pause longer", "Project louder")

Start immediately: {"pace": 50, "clarity": 50, "energy": 50, "filler_count": 0, "insight": "Session started, warming up", "action": "Begin speaking now"}
"""

ROOM_READ_INSTRUCTION = """
You are StageSense AudienceRead — real-time audience intelligence.
You receive live video of an audience during a presentation.

YOUR ONLY JOB: Every 3 seconds, output a JSON audience report and nothing else.

OUTPUT FORMAT — speak exactly this JSON, nothing before or after:
{"engagement": <0-100>, "confusion": <0-100>, "excitement": <0-100>, "alert": "<15 words max>"}

SCORING:
- engagement: 100=fully attentive and focused on the speaker
- confusion: 100=many lost, blank, or frustrated faces (HIGH = BAD)
- excitement: 100=leaning forward, nodding, smiling
- alert: one specific observation for the speaker

Start immediately: {"engagement": 50, "confusion": 0, "excitement": 50, "alert": "Session started, scanning audience now"}
"""

# ADK Agents — global singletons (L3 pattern)
_coach_agent = Agent(name="stagesense_coach", model=MODEL_ID, instruction=COACH_INSTRUCTION)
_room_agent = Agent(name="stagesense_roomread", model=MODEL_ID, instruction=ROOM_READ_INSTRUCTION)
_session_service = InMemorySessionService()


class StageSenseAgent:
    def __init__(self):
        logger.info(f"StageSenseAgent ready — model: {MODEL_ID}")

    async def run_session(
        self,
        websocket,
        get_mode: Callable[[], str],
    ) -> AsyncIterator[dict]:
        """
        Streams parsed score dicts from Gemini Live via ADK Runner.
        Exact L3 pattern: Runner + LiveRequestQueue + asyncio.gather peers.
        """
        mode = get_mode()
        agent = _coach_agent if mode == "coach" else _room_agent
        user_id = "presenter"
        session_id = f"ss-{asyncio.get_event_loop().time():.0f}"

        await _session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

        runner = Runner(
            app_name=APP_NAME,
            agent=agent,
            session_service=_session_service,
        )

        live_request_queue = LiveRequestQueue()
        score_queue: asyncio.Queue[dict] = asyncio.Queue()

        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=["AUDIO"],
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            session_resumption=types.SessionResumptionConfig(),
        )

        logger.info(f"Opening Gemini Live — mode={mode}, model={MODEL_ID}")

        async def upstream():
            """Reads WebSocket frames → LiveRequestQueue."""
            try:
                while True:
                    msg = await websocket.receive()
                    if msg.get("type") == "websocket.disconnect":
                        logger.info("WebSocket disconnected")
                        break
                    data = msg.get("bytes")
                    if data:
                        if data[:4] == b"VID:":
                            blob = types.Blob(data=data[4:], mime_type="image/jpeg")
                        else:
                            blob = types.Blob(data=data, mime_type="audio/pcm;rate=16000")
                        live_request_queue.send_realtime(blob)
            except Exception as e:
                logger.info(f"Upstream ended: {type(e).__name__}")
            finally:
                live_request_queue.close()

        async def downstream():
            """Reads ADK events → parses JSON → score_queue."""
            logger.info("Connecting to Gemini Live via ADK Runner...")
            async for event in runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=live_request_queue,
                run_config=run_config,
            ):
                output_tx = getattr(event, "output_audio_transcription", None)
                if output_tx and getattr(output_tx, "final_transcript", None):
                    tx = output_tx.final_transcript
                    logger.info(f"Transcript: {tx[:80]!r}")
                    scores = _parse_scores(tx, mode)
                    if scores:
                        await score_queue.put(scores)

                sc = getattr(event, "server_content", None)
                if sc and getattr(sc, "model_turn", None):
                    for part in sc.model_turn.parts:
                        if getattr(part, "text", None):
                            logger.info(f"Text: {part.text[:80]!r}")
                            scores = _parse_scores(part.text, mode)
                            if scores:
                                await score_queue.put(scores)

        gather_task = asyncio.create_task(
            asyncio.gather(upstream(), downstream(), return_exceptions=True)
        )

        try:
            while not gather_task.done():
                try:
                    scores = await asyncio.wait_for(score_queue.get(), timeout=1.0)
                    yield scores
                except asyncio.TimeoutError:
                    continue
        finally:
            gather_task.cancel()
            try:
                await gather_task
            except (asyncio.CancelledError, Exception):
                pass
            logger.info("Session complete")


def _parse_scores(text: str, mode: str) -> dict | None:
    """Robust JSON extraction — first-brace to last-brace."""
    stripped = text.strip()
    try:
        start = stripped.find("{")
        end = stripped.rfind("}") + 1
        if start >= 0 and end > start:
            scores = json.loads(stripped[start:end])
            scores["mode"] = mode
            return scores
    except json.JSONDecodeError:
        pass
    for line in stripped.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            scores = json.loads(line)
            scores["mode"] = mode
            return scores
        except json.JSONDecodeError:
            continue
    return None
