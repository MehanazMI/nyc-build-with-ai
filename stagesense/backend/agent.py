"""
StageSense Agent — agent.py
Two ADK agents powered by Gemini Live:
  - CoachAgent: analyzes speaker delivery
  - RoomReadAgent: reads audience engagement
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
MODEL = "gemini-live-2.5-flash-preview-native-audio"

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
- Output ONLY valid JSON, one object per line
- Keep insight and action under 12 words each
- Be encouraging but honest
- Whisper the "action" field as gentle real-time guidance
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
- Output ONLY valid JSON, one object per line
- Keep alert under 15 words
- Be specific about what you observe
- Whisper the "alert" as a quiet, calm guidance to the presenter
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
        """
        mode = get_mode()
        instruction = COACH_INSTRUCTION if mode == "coach" else ROOM_READ_INSTRUCTION

        config = genai_types.LiveConnectConfig(
            response_modalities=["AUDIO", "TEXT"],
            system_instruction=instruction,
            speech_config=genai_types.SpeechConfig(
                voice_config=genai_types.VoiceConfig(
                    prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(
                        voice_name="Aoede"
                    )
                )
            ),
        )

        async with self.client.aio.live.connect(model=MODEL, config=config) as session:
            logger.info(f"Gemini Live session opened — mode: {mode}")

            # Fan-out: receive from mobile WebSocket, send to Gemini Live
            async def upstream():
                try:
                    while True:
                        data = await websocket.receive_bytes()
                        # Data is raw PCM audio or video frame bytes
                        # Detect type by header or content type prefix
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
                    logger.warning(f"Upstream ended: {e}")

            upstream_task = asyncio.create_task(upstream())

            try:
                async for response in session.receive():
                    # Check for text output with JSON scores
                    if response.server_content and response.server_content.model_turn:
                        for part in response.server_content.model_turn.parts:
                            if part.text:
                                scores = self._parse_scores(part.text, mode)
                                if scores:
                                    yield scores
            finally:
                upstream_task.cancel()
                logger.info("Gemini Live session closed")

    def _parse_scores(self, text: str, mode: str) -> dict | None:
        """Extract JSON score dict from Gemini text output."""
        for line in text.strip().splitlines():
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
