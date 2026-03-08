---
name: voice-ai-development
description: Build real-time voice AI systems using OpenAI Realtime API, Vapi, Deepgram STT, and ElevenLabs TTS. Covers streaming pipelines, VAD, barge-in detection, and provider mixing.
---

# Voice AI Development

## Capabilities
- OpenAI Realtime API (native voice-to-voice)
- Vapi voice agents (hosted, phone + web)
- Deepgram STT / TTS (real-time streaming)
- ElevenLabs voice synthesis (streaming, low-latency)
- LiveKit real-time infrastructure
- WebRTC audio handling
- Voice agent design
- Latency optimization

## Requirements
- Python or Node.js
- API keys for providers
- Audio handling knowledge

---

## Patterns

### OpenAI Realtime API — Native voice-to-voice with GPT-4o

**When to use**: When you want integrated voice AI without separate STT/TTS.

```python
import asyncio
import websockets
import json
import base64

OPENAI_API_KEY = "sk-..."

async def voice_session():
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }
    async with websockets.connect(url, extra_headers=headers) as ws:
        # Configure session
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500
                },
            }
        }))

        # Send audio (PCM16, 24kHz, mono)
        async def send_audio(audio_bytes):
            await ws.send(json.dumps({
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(audio_bytes).decode()
            }))

        # Receive events
        async for message in ws:
            event = json.loads(message)
            # handle event types: response.audio.delta, response.done, etc.
```

---

### Deepgram STT + ElevenLabs TTS — Best-in-class transcription and synthesis

**When to use**: High quality voice, custom pipeline control.

```python
import asyncio
from deepgram import DeepgramClient, LiveTranscriptionEvents
from elevenlabs import ElevenLabs

# Deepgram real-time transcription
deepgram = DeepgramClient(api_key="...")

async def transcribe_stream(audio_stream):
    connection = deepgram.listen.live.v("1")

    async def on_transcript(result):
        transcript = result.channel.alternatives[0].transcript
        if transcript and result.is_final:
            await handle_user_input(transcript)

    connection.on(LiveTranscriptionEvents.Transcript, on_transcript)
    await connection.start({
        "model": "nova-2",
        "language": "en",
        "smart_format": True,
        "interim_results": True,
        "vad_events": True,
        "encoding": "linear16",
        "sample_rate": 16000
    })

    async for chunk in audio_stream:
        await connection.send(chunk)
    await connection.finish()

# ElevenLabs streaming TTS
eleven = ElevenLabs(api_key="...")

def text_to_speech_stream(text: str):
    """Stream TTS audio chunks."""
    audio_stream = eleven.text_to_speech.convert_as_stream(
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
        model_id="eleven_turbo_v2_5",      # Fastest
        text=text,
        output_format="pcm_24000"          # Raw PCM for low latency
    )
    for chunk in audio_stream:
        yield chunk
```

---

## Anti-Patterns

### ❌ Non-streaming Pipeline
**Why bad**: Adds seconds of latency. User perceives as slow. Loses conversation flow.
**Instead**: Stream everything — STT interim results, LLM token streaming, TTS chunk streaming. Start TTS before LLM finishes.

### ❌ Ignoring Interruptions
**Why bad**: Frustrating UX. Feels like talking to a machine.
**Instead**: Implement barge-in detection. Use VAD to detect user speech. Stop TTS immediately. Clear audio queue.

### ❌ Single Provider Lock-in
**Why bad**: May not be best quality. Single point of failure.
**Instead**: Mix best providers:
- Deepgram for STT (speed + accuracy)
- ElevenLabs for TTS (voice quality)
- OpenAI/Gemini for LLM

## Limitations
- Latency varies by provider
- Cost per minute adds up
- Quality depends on network
- Complex debugging

## When to Use
Use this skill when building voice conversation UIs, voice agents, real-time audio streaming, or integrating STT/TTS pipelines.
