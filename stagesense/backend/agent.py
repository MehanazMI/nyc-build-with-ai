"""
StageSense Agent — agent.py
Two modes powered by Gemini Live:
  - coach: analyzes speaker delivery
  - roomread: reads audience engagement

FIXED (Pass 3):
  - Bug 4:  Switch to half-cascade model (gemini-2.0-flash-live-001), TEXT modality
  - Bug 5:  Robust JSON parsing (first-brace extraction)
  - Bug 13: asyncio.gather concurrency pattern — prevents session.receive() deadlock
  - Bug 14: Initial stimulus sent immediately after session opens
"""
import asyncio
import json
import logging
import os
from typing import AsyncIterator, Callable

from google import genai
from google.genai import types as genai_types

logger = logging.getLogger("stagesense.agent")

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "ai-hack-489018")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

# Bug 4 FIX: Switch to half-cascade model which supports TEXT response modality.
# Native audio model (gemini-live-2.5-flash-preview-native-audio) ONLY supports AUDIO.
# For clean JSON output on dashboard, half-cascade is the right choice.
MODEL = "gemini-2.0-flash-live-001"

# ─── Instructions ─────────────────────────────────────────────────────────────

COACH_INSTRUCTION = """
You are StageSense Coach — a real-time presentation coach.
You receive live audio and video of a presenter.

Analyze continuously and every 5 seconds output a JSON object on its own line:
{
  "pace": <0-100 score for speaking speed — 100 is ideal>,
  "clarity": <0-100 score for articulation and word choice>,
  "energy": <0-100 score for vocal energy and confidence>,
  "filler_count": <number of filler words ("um","uh","like","you know") in last 30 seconds>,
  "insight": "<one specific, concrete coaching observation>",
  "action": "<one short immediate action for the presenter, e.g. 'Slow down', 'Pause here', 'Add an example'>"
}

Rules:
- Output ONLY valid JSON, one object per line. No other text.
- Keep insight and action under 12 words each
- Be encouraging but honest
"""

ROOM_READ_INSTRUCTION = """
You are StageSense AudienceRead — a real-time audience intelligence system.
You receive live video of an audience during a presentation.

Analyze faces, body language, and attention signals every 3 seconds.
Output a JSON object on its own line:
{
  "engagement": <0-100, how attentive and focused the audience is>,
  "confusion": <0-100, how many look lost, confused, or disengaged>,
  "excitement": <0-100, how many are leaning forward, nodding, smiling>,
  "alert": "<one actionable alert for the speaker, e.g. 'Row 2 losing interest — add an example now'>"
}

Rules:
- Output ONLY valid JSON, one object per line. No other text.
- Keep alert under 15 words
- Be specific about what you observe
"""


# ─── StageSense Agent ─────────────────────────────────────────────────────────

class StageSenseAgent:
    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=PROJECT,
            location=LOCATION,
        )

    async def run_session(
        self,
        websocket,
        get_mode: Callable[[], str],
    ) -> AsyncIterator[dict]:
        """
        Opens a Gemini Live session and streams parsed score dicts.
        Receives audio+video frames from the mobile WebSocket.

        Bug 13 FIX: Uses asyncio.gather() so upstream and downstream cancel
        each other on disconnect. Previous pattern (task + async for) caused
        session.receive() to hang indefinitely after WebSocket disconnect.

        Bug 14 FIX: Sends an initial stimulus immediately after session opens
        so Gemini starts analyzing right away instead of waiting for input.
        """
        mode = get_mode()
        instruction = COACH_INSTRUCTION if mode == "coach" else ROOM_READ_INSTRUCTION

        # Bug 4 FIX: TEXT modality — works with half-cascade gemini-2.0-flash-live-001
        config = genai_types.LiveConnectConfig(
            response_modalities=["TEXT"],
            system_instruction=instruction,
        )

        score_queue: asyncio.Queue[dict] = asyncio.Queue()

        async with self.client.aio.live.connect(model=MODEL, config=config) as session:
            logger.info(f"Gemini Live session opened — mode: {mode}, model: {MODEL}")

            # Bug 14 FIX: Wake the model immediately so it starts analyzing
            # without waiting for audio input.
            try:
                await session.send_client_content(
                    turns=genai_types.Content(
                        parts=[genai_types.Part(text="Session started. Begin analyzing now.")]
                    ),
                    turn_complete=True,
                )
                logger.info("Initial stimulus sent — model awakened")
            except Exception as e:
                logger.warning(f"Initial stimulus failed (non-fatal): {e}")

            # Bug 13 FIX: Both upstream and downstream as true peer coroutines.
            # asyncio.gather ensures if upstream dies (WS disconnect), downstream
            # is cancelled immediately — no more hanging session.receive() loops.
            async def upstream():
                try:
                    while True:
                        data = await websocket.receive_bytes()
                        if data[:4] == b"VID:":
                            blob = genai_types.Blob(
                                data=data[4:],
                                mime_type="image/jpeg",
                            )
                        else:
                            blob = genai_types.Blob(
                                data=data,
                                mime_type="audio/pcm;rate=16000",
                            )
                        await session.send_realtime_input(media=blob)
                except Exception as e:
                    logger.info(f"Upstream ended: {e}")

            async def downstream():
                try:
                    async for response in session.receive():
                        if response.server_content and response.server_content.model_turn:
                            for part in response.server_content.model_turn.parts:
                                if part.text:
                                    scores = self._parse_scores(part.text, mode)
                                    if scores:
                                        await score_queue.put(scores)
                except Exception as e:
                    logger.info(f"Downstream ended: {e}")

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
                logger.info("Gemini Live session closed")

    def _parse_scores(self, text: str, mode: str) -> dict | None:
        """
        Bug 5 FIX: Robust JSON extraction using first/last brace positions.
        Handles multi-line JSON, mixed prose, and partial outputs.
        """
        stripped = text.strip()
        # Primary: find first { ... } block (handles multi-line JSON)
        try:
            start = stripped.find("{")
            end = stripped.rfind("}") + 1
            if start >= 0 and end > start:
                scores = json.loads(stripped[start:end])
                scores["mode"] = mode
                return scores
        except json.JSONDecodeError:
            pass
        # Fallback: line-by-line scan for single-line JSON
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
        logger.debug(f"No JSON found in: {text[:80]!r}")
        return None
