"""
StageSense Agent — agent.py

FIXED (4 root causes):
  #1  Model ID:   gemini-live-2.5-flash-preview-native-audio-09-2025 → DISCONTINUED.
                  Default now: gemini-2.5-flash-preview-native-audio
  #2  Stimulus:   Pre-session Hello removed. For native-audio + ADK 1.24.1, sending
                  content BEFORE run_live yields an empty turn and closes (Code 1000).
                  Incoming audio naturally drives the first turn.
  #3  Dual-auth:  When GOOGLE_API_KEY is set, bypass ADK Runner entirely and use
                  client.aio.live.connect() directly with TEXT modality (half-cascade).
                  ADK Runner routes through Vertex bidiGenerateContent regardless of
                  the API key — causing 1008 if project isn't allowlisted.
  #4  Nothing to  Fix here — requirements.txt is pinned separately.

Architecture (Vertex path — ADK Runner):
  runner.run_live() → downstream() captures output_audio_transcription + server_content
  upstream() pumps WS frames → LiveRequestQueue
  asyncio.gather(upstream, downstream) as peer tasks — prevent deadlock on disconnect

Architecture (AI Studio path — Direct Connect):
  client.aio.live.connect() → TEXT modality (half-cascade model)
  upstream() pumps WS frames → session.send_realtime()
  downstream() reads session.receive() → parses JSON
"""
import asyncio
import json
import logging
import os
import warnings
from typing import AsyncIterator, Callable

import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(override=True)  # MUST run before any genai/ADK import

# Suppress pydantic serialization warnings from ADK
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

logger = logging.getLogger("stagesense.agent")

APP_NAME = "stagesense"

# ── Model selection ───────────────────────────────────────────────────────────
# Fix #1: default to current stable Vertex model — the -09-2025 suffix was
#         discontinued Oct 18 2025 and returns 1000/1008 for every session.
_API_KEY = os.getenv("GOOGLE_API_KEY", "")
_USE_VERTEX = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"

if _USE_VERTEX or not _API_KEY:
    # Vertex path: native audio, AUDIO modality, ADK Runner
    # Use VERTEX_MODEL_ID first, then MODEL_ID, then safe default
    MODEL_ID = (
        os.getenv("VERTEX_MODEL_ID")
        or os.getenv("MODEL_ID", "gemini-2.5-flash-preview-native-audio")
    )
    _AUTH_MODE = "vertex"
else:
    # AI Studio path: native audio models, AUDIO modality.
    # REST API confirmed these models support bidiGenerateContent:
    #   gemini-2.5-flash-native-audio-latest (active)
    #   gemini-2.5-flash-native-audio-preview-09-2025
    #   gemini-2.5-flash-native-audio-preview-12-2025
    # The API key does NOT have gemini-2.0-flash-live-001 — 404.
    # Use MODEL_ID from .env (set to gemini-2.5-flash-native-audio-latest)
    MODEL_ID = (
        os.getenv("APIKEY_MODEL_ID")
        or os.getenv("MODEL_ID", "gemini-2.5-flash-native-audio-latest")
    )
    _AUTH_MODE = "api_key"

logger.info(f"StageSense agent — auth={_AUTH_MODE}, model={MODEL_ID}")

COACH_INSTRUCTION = (
    "You are a JSON-only presentation scorecard API. "
    "RULES: Output ONLY raw JSON. Never output prose, markdown, explanations, or any other text. "
    "FORBIDDEN: do not use ** or *, do not write sentences, do not say 'I', do not say 'StageSense'. "
    "Every response must be exactly this JSON object and nothing else: "
    '{"pace": <0-100>, "clarity": <0-100>, "energy": <0-100>, "filler_count": <integer>, "insight": "<10 words>", "action": "<10 words>"} '
    "Scoring: pace=speaking speed (100=ideal), clarity=articulation (100=crisp), energy=confidence (100=high), filler_count=um/uh/like count. "
    "Output your first scorecard NOW: "
    '{"pace": 50, "clarity": 50, "energy": 50, "filler_count": 0, "insight": "Session started", "action": "Begin speaking"}'
)

ROOM_READ_INSTRUCTION = (
    "You are a JSON-only audience scorecard API. "
    "RULES: Output ONLY raw JSON. Never output prose, markdown, explanations, or any other text. "
    "FORBIDDEN: do not use ** or *, do not write sentences, do not say 'I'. "
    "Every response must be exactly this JSON object and nothing else: "
    '{"engagement": <0-100>, "confusion": <0-100>, "excitement": <0-100>, "alert": "<10 words>"} '
    "Scoring: engagement=attention level, confusion=lost faces (100=bad), excitement=energy in room. "
    "Output your first scorecard NOW: "
    '{"engagement": 60, "confusion": 10, "excitement": 50, "alert": "Scanning audience now"}'
)


# ── Vertex path: ADK Runner setup (lazy import to avoid SDK init before dotenv) ──
def _get_vertex_runner(mode: str):
    """Lazy-init ADK Runner+Agent for Vertex path."""
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService

    instruction = COACH_INSTRUCTION if mode == "coach" else ROOM_READ_INSTRUCTION
    agent_name = f"stagesense_{mode}"
    agent = Agent(name=agent_name, model=MODEL_ID, instruction=instruction)
    session_service = InMemorySessionService()
    runner = Runner(app_name=APP_NAME, agent=agent, session_service=session_service)
    return runner, session_service


class StageSenseAgent:
    def __init__(self):
        logger.info(f"StageSenseAgent ready — auth={_AUTH_MODE}, model={MODEL_ID}")

    async def run_session(
        self,
        websocket,
        get_mode: Callable[[], str],
    ) -> AsyncIterator[dict]:
        """
        Dispatch to the correct auth path:
          - Vertex  → _run_vertex_session (ADK Runner + AUDIO modality)
          - API Key → _run_apikey_session (direct connect + TEXT modality)
        """
        mode = get_mode()
        if _AUTH_MODE == "vertex":
            async for scores in self._run_vertex_session(websocket, mode):
                yield scores
        else:
            async for scores in self._run_apikey_session(websocket, mode):
                yield scores

    # ── Vertex path ─────────────────────────────────────────────────────────

    async def _run_vertex_session(
        self, websocket, mode: str
    ) -> AsyncIterator[dict]:
        """
        ADK Runner + native audio + AUDIO modality (Vertex AI).
        Fix #2: NO pre-session Hello — removed entirely.
                Incoming audio/video naturally drives the first turn.
        Fix #1: MODEL_ID is now the current stable identifier.
        """
        from google.adk.agents.live_request_queue import LiveRequestQueue
        from google.adk.agents.run_config import RunConfig, StreamingMode

        runner, session_service = _get_vertex_runner(mode)
        user_id = "presenter"
        session_id = f"ss-{asyncio.get_event_loop().time():.0f}"

        await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=["AUDIO"],
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            session_resumption=types.SessionResumptionConfig(),
            proactivity=types.ProactivityConfig(proactive_audio=True),
        )

        live_request_queue = LiveRequestQueue()
        score_queue: asyncio.Queue[dict] = asyncio.Queue()

        # Fix #2: NO pre-session stimulus — removed.
        # Native audio on ADK 1.24.1: sending content before run_live yields
        # an empty turn + immediate Code 1000 close. Audio drives the first turn.

        async def upstream():
            try:
                while True:
                    msg = await websocket.receive()
                    if msg.get("type") == "websocket.disconnect":
                        logger.info("WS disconnected (upstream)")
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
            logger.info("Connecting to Gemini Live via ADK Runner (Vertex)...")
            async for event in runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=live_request_queue,
                run_config=run_config,
            ):
                # Path 1: output_audio_transcription (primary for native audio on Vertex)
                output_tx = getattr(event, "output_audio_transcription", None)
                if output_tx and getattr(output_tx, "final_transcript", None):
                    tx = output_tx.final_transcript
                    logger.info(f"Transcript: {tx[:80]!r}")
                    scores = _parse_scores(tx, mode)
                    if scores:
                        await score_queue.put(scores)

                # Path 2: ADK event content (text parts)
                content = getattr(event, "content", None)
                if content and getattr(content, "parts", None):
                    for part in content.parts:
                        if getattr(part, "text", None):
                            logger.info(f"Content text: {part.text[:80]!r}")
                            scores = _parse_scores(part.text, mode)
                            if scores:
                                await score_queue.put(scores)

                # Path 3: server_content fallback
                sc = getattr(event, "server_content", None)
                if sc and getattr(sc, "model_turn", None):
                    for part in sc.model_turn.parts:
                        if getattr(part, "text", None):
                            logger.info(f"Server text: {part.text[:80]!r}")
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
            logger.info("Vertex session complete")

    # ── AI Studio / API Key path ─────────────────────────────────────────────

    async def _run_apikey_session(
        self, websocket, mode: str
    ) -> AsyncIterator[dict]:
        """
        Fix #3 (revised): Use ADK Runner with GOOGLE_GENAI_USE_VERTEXAI forced to
        'false' in os.environ BEFORE creating the Runner/Agent.

        Why: google-genai==1.56.0 direct connect (client.aio.live.connect) has model
        path resolution issues — it prepends 'models/' causing 1008 even on v1alpha.
        The ADK Runner handles this internally when vertexai=False is in the env.

        This is the proven approach from way-back-home L3 and the original test_api_key.py.
        Uses TEXT modality for the half-cascade model (cleaner JSON, no AUDIO needed).
        """
        # Force AI Studio SDK path — must happen before Agent/Runner are created
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"
        os.environ["GOOGLE_API_KEY"] = _API_KEY

        from google.adk.agents import Agent
        from google.adk.agents.live_request_queue import LiveRequestQueue
        from google.adk.agents.run_config import RunConfig, StreamingMode

        instruction = COACH_INSTRUCTION if mode == "coach" else ROOM_READ_INSTRUCTION
        agent_name = f"stagesense_{mode}_apikey"
        agent = Agent(name=agent_name, model=MODEL_ID, instruction=instruction)
        from google.adk.sessions import InMemorySessionService
        from google.adk.runners import Runner
        session_service = InMemorySessionService()
        runner = Runner(app_name=APP_NAME, agent=agent, session_service=session_service)

        user_id = "presenter"
        session_id = f"ss-ak-{asyncio.get_event_loop().time():.0f}"

        await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

        # AUDIO modality: gemini-2.5-flash-native-audio-latest is native-audio only.
        # REST API confirmed: it supports bidiGenerateContent. TEXT modality → 1007.
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=["AUDIO"],
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            proactivity=types.ProactivityConfig(proactive_audio=True),
        )

        live_request_queue = LiveRequestQueue()
        score_queue: asyncio.Queue[dict] = asyncio.Queue()

        # Prime the session with a text stimulus so the model starts outputting
        # Without this, native-audio model waits for audio VAD before first response
        live_request_queue.send_content(
            types.Content(parts=[types.Part(text="Begin analysis. Output your JSON scorecard now.")])
        )

        logger.info(f"Connecting to Gemini Live via ADK Runner (AI Studio) model={MODEL_ID}...")


        async def upstream():
            try:
                while True:
                    msg = await websocket.receive()
                    if msg.get("type") == "websocket.disconnect":
                        logger.info("WS disconnected (upstream)")
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

        # Buffer for streaming text fragments from the model
        text_buffer = _TextAccumulator(mode)

        async def downstream():
            logger.info("✅ Gemini Live session open (AI Studio, ADK Runner)")
            async for event in runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=live_request_queue,
                run_config=run_config,
            ):
                # Path 1: output_audio_transcription
                output_tx = getattr(event, "output_audio_transcription", None)
                if output_tx and getattr(output_tx, "final_transcript", None):
                    tx = output_tx.final_transcript
                    logger.info(f"Transcript: {tx[:80]!r}")
                    for scores in text_buffer.feed(tx):
                        await score_queue.put(scores)

                # Path 2: server_content model_turn parts
                sc = getattr(event, "server_content", None)
                if sc and getattr(sc, "model_turn", None):
                    for part in sc.model_turn.parts:
                        if getattr(part, "text", None):
                            for scores in text_buffer.feed(part.text):
                                await score_queue.put(scores)

                # Path 3: content parts (streaming tokens arrive here)
                content = getattr(event, "content", None)
                if content and getattr(content, "parts", None):
                    for part in content.parts:
                        if getattr(part, "text", None):
                            for scores in text_buffer.feed(part.text):
                                await score_queue.put(scores)

        upstream_task = asyncio.create_task(upstream())
        downstream_task = asyncio.create_task(downstream())

        try:
            # Exit as soon as upstream (WS) closes — cancel downstream immediately
            while not upstream_task.done():
                try:
                    scores = await asyncio.wait_for(score_queue.get(), timeout=0.5)
                    yield scores
                except asyncio.TimeoutError:
                    continue
            # WS closed — cancel downstream right away to stop ADK runner
            downstream_task.cancel()
            # Drain any scores that arrived just before disconnect
            while not score_queue.empty():
                yield score_queue.get_nowait()
        except Exception as e:
            logger.error(f"API key session error: {type(e).__name__}: {e}")
        finally:
            upstream_task.cancel()
            downstream_task.cancel()
            for t in [upstream_task, downstream_task]:
                try:
                    await t
                except (asyncio.CancelledError, Exception):
                    pass
            logger.info("API Key session complete")




class _TextAccumulator:
    """
    Buffers streaming text fragments and yields complete JSON score dicts.

    The native-audio model streams JSON as tiny token fragments across many events:
        Event 1: '{'
        Event 2: '"pace"'
        Event 3: ': 75,'
        ...
        Event N: '}'

    This class accumulates fragments, detects complete JSON objects by matching
    braces, and yields parsed score dicts.
    """

    def __init__(self, mode: str):
        self.mode = mode
        self.buffer = ""
        self.brace_depth = 0

    def feed(self, text: str) -> list[dict]:
        """Feed a text fragment. Returns list of complete score dicts (0 or more)."""
        results = []
        for ch in text:
            if ch == "{":
                if self.brace_depth == 0:
                    self.buffer = ""  # Start fresh for new object
                self.brace_depth += 1
            if self.brace_depth > 0:
                self.buffer += ch
            if ch == "}":
                self.brace_depth -= 1
                if self.brace_depth == 0 and self.buffer:
                    # Try to parse the complete object
                    scores = _parse_scores(self.buffer, self.mode)
                    if scores:
                        logger.info(f"Parsed scores: {scores}")
                        results.append(scores)
                    self.buffer = ""
        return results


def _parse_scores(text: str, mode: str) -> dict | None:
    """Parse a complete JSON string into a score dict."""
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
    return None
