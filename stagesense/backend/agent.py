"""
StageSense Agent — agent.py
Two modes powered by Gemini Live API via ADK Runner:
  - coach: analyzes speaker delivery (pace, clarity, energy, fillers)
  - roomread: reads audience engagement (engagement, confusion, excitement)

Uses the PROVEN Way Back Home L3/L4 ADK Runner pattern:
  - Runner + InMemorySessionService + LiveRequestQueue
  - Native audio model: gemini-live-2.5-flash-preview-native-audio-09-2025
  - AUDIO modality with output_audio_transcription to capture JSON text
  - asyncio.gather(upstream, downstream) peer pattern — no deadlocks

The JSON scoring is captured from output_audio_transcription.final_transcript,
NOT from audio bytes — so the model speaks JSON and we transcribe it.
"""
import asyncio
import json
import logging
import os
from typing import AsyncIterator, Callable

from google.adk.agents.llm_agent import Agent
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

logger = logging.getLogger("stagesense.agent")

APP_NAME = "stagesense"

# The proven Vertex AI model from Way Back Home L3/L4
MODEL_ID = os.getenv("MODEL_ID", "gemini-live-2.5-flash-preview-native-audio-09-2025")

# ─── Instructions ─────────────────────────────────────────────────────────────

COACH_INSTRUCTION = """
You are StageSense Coach — a real-time presentation coach.
You receive live audio and video of a presenter.

Analyze continuously. Every 5 seconds, SPEAK a JSON object and nothing else:
{"pace": <0-100>, "clarity": <0-100>, "energy": <0-100>, "filler_count": <integer>, "insight": "<max 12 words>", "action": "<max 12 words, immediate tip>"}

Rules:
- Speak ONLY the JSON object. No greeting, no commentary, just the JSON.
- pace: 100 = ideal speed, 0 = too fast or silent
- clarity: 100 = crisp and articulate
- energy: 100 = confident, engaged
- filler_count: count of "um", "uh", "like", "you know" in last 30 seconds
- action: one short, specific coaching cue (e.g. "Slow down", "Add a pause", "Project louder")
"""

ROOM_READ_INSTRUCTION = """
You are StageSense AudienceRead — real-time audience intelligence.
You receive live video of an audience during a presentation.

Analyze faces, body language, and attention every 3 seconds. SPEAK a JSON object and nothing else:
{"engagement": <0-100>, "confusion": <0-100>, "excitement": <0-100>, "alert": "<max 15 words, specific observation>"}

Rules:
- Speak ONLY the JSON object. No greeting, no commentary, just the JSON.
- engagement: 100 = fully attentive
- confusion: 100 = many confused faces (high confusion = bad)
- excitement: 100 = leaning forward, nodding, smiling
- alert: one specific observation for the speaker (e.g. "Row 2 losing interest — add an example")
"""


# ─── StageSense Agent ─────────────────────────────────────────────────────────

class StageSenseAgent:
    def __init__(self):
        self._session_service = InMemorySessionService()

    def _build_runner(self, mode: str) -> Runner:
        instruction = COACH_INSTRUCTION if mode == "coach" else ROOM_READ_INSTRUCTION
        agent = Agent(
            model=MODEL_ID,
            name=f"stagesense_{mode}",
            description=f"StageSense {mode} mode agent",
            instruction=instruction,
        )
        return Runner(
            app_name=APP_NAME,
            agent=agent,
            session_service=self._session_service,
        )

    async def run_session(
        self,
        websocket,
        get_mode: Callable[[], str],
    ) -> AsyncIterator[dict]:
        """
        Opens a Gemini Live session via ADK Runner and yields parsed score dicts.

        Concurrency pattern: asyncio.gather(upstream, downstream) — if the WebSocket
        disconnects, both tasks cancel each other immediately (no deadlock).

        JSON is captured from output_audio_transcription.final_transcript because
        the native audio model speaks its response; we transcribe that speech to text.
        """
        mode = get_mode()
        runner = self._build_runner(mode)

        # Create a fresh session for this connection
        user_id = "presenter"
        session_id = f"session-{asyncio.get_event_loop().time():.0f}"
        await self._session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

        live_request_queue = LiveRequestQueue()
        score_queue: asyncio.Queue[dict] = asyncio.Queue()

        # RunConfig: native audio model needs AUDIO modality + transcription config
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=["AUDIO"],
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            session_resumption=types.SessionResumptionConfig(),
        )

        # Bug 14 FIX: Send initial stimulus to wake the model immediately
        logger.info(f"Sending initial stimulus — mode: {mode}, model: {MODEL_ID}")
        live_request_queue.send_content(
            types.Content(parts=[types.Part(text="Session started. Begin analyzing now.")])
        )

        async def upstream():
            """Reads audio/video bytes from WebSocket → LiveRequestQueue."""
            try:
                while True:
                    data = await websocket.receive_bytes()
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
            """Reads ADK events → parses JSON from transcription → score_queue."""
            logger.info("Connecting to Gemini Live via ADK Runner...")
            async for event in runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=live_request_queue,
                run_config=run_config,
            ):
                # Capture JSON from output audio transcription (the model speaks JSON)
                output_transcription = getattr(event, "output_audio_transcription", None)
                if output_transcription and output_transcription.final_transcript:
                    transcript = output_transcription.final_transcript
                    logger.debug(f"Transcript: {transcript[:100]!r}")
                    scores = self._parse_scores(transcript, mode)
                    if scores:
                        await score_queue.put(scores)

                # Also check server_content parts for TEXT modality fallback
                if hasattr(event, "server_content") and event.server_content:
                    if event.server_content.model_turn:
                        for part in event.server_content.model_turn.parts:
                            if part.text:
                                scores = self._parse_scores(part.text, mode)
                                if scores:
                                    await score_queue.put(scores)

        # Bug 13 FIX: asyncio.gather so both tasks cancel each other on disconnect
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
            except asyncio.CancelledError:
                pass
            logger.info("Session complete")

    def _parse_scores(self, text: str, mode: str) -> dict | None:
        """
        Bug 5 FIX: Robust JSON extraction — first/last brace positions.
        Handles multi-line JSON and prose wrapping.
        """
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
        # Fallback: line-by-line
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
