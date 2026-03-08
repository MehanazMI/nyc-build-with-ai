---
name: voice-ai-engine-development
description: Build production-ready voice AI engines with real-time conversation using async worker pipelines, interrupt handling, and multi-provider support (Deepgram, ElevenLabs, OpenAI, Gemini). Based on Vocode architecture patterns.
---

# Voice AI Engine Development

## Overview
This skill guides you through building production-ready voice AI engines with real-time conversation capabilities. The core architecture uses an **async queue-based worker pipeline** where each component runs independently and communicates via `asyncio.Queue` objects.

## When to Use
- Building real-time voice conversation systems
- Implementing voice assistants or chatbots
- Creating voice-enabled agents with interrupt capabilities
- Integrating multiple transcription, LLM, or TTS providers
- Working with streaming audio processing pipelines
- User mentions Vocode, voice engines, or conversational AI

---

## Core Architecture — The Worker Pipeline

```
Audio In → Transcriber → Agent → Synthesizer → Audio Out
          (Worker 1)  (Worker 2) (Worker 3)
```

**Key Benefits:**
- **Decoupling**: Workers only know about their input/output queues
- **Concurrency**: All workers run simultaneously via `asyncio`
- **Backpressure**: Queues automatically handle rate differences
- **Interruptibility**: Everything can be stopped mid-stream

### Base Worker Pattern

```python
class BaseWorker:
    def __init__(self, input_queue, output_queue):
        self.input_queue = input_queue   # asyncio.Queue to consume from
        self.output_queue = output_queue  # asyncio.Queue to produce to
        self.active = False

    def start(self):
        self.active = True
        asyncio.create_task(self._run_loop())

    async def _run_loop(self):
        while self.active:
            item = await self.input_queue.get()
            await self.process(item)

    async def process(self, item):
        raise NotImplementedError

    def terminate(self):
        self.active = False
```

---

## Component Guide

### 1. Transcriber (Audio → Text)

```python
class BaseTranscriber:
    def __init__(self, transcriber_config):
        self.input_queue = asyncio.Queue()   # Audio chunks (bytes)
        self.output_queue = asyncio.Queue()  # Transcription objects
        self.is_muted = False

    def send_audio(self, chunk: bytes):
        if not self.is_muted:
            self.input_queue.put_nowait(chunk)
        else:
            self.input_queue.put_nowait(self.create_silent_chunk(len(chunk)))

    def mute(self):
        """Called when bot starts speaking — prevents echo."""
        self.is_muted = True

    def unmute(self):
        self.is_muted = False
```

**Output Format:**
```python
class Transcription:
    message: str       # "Hello, how are you?"
    confidence: float  # 0.95
    is_final: bool     # True = complete sentence
    is_interrupt: bool # Set by TranscriptionsWorker
```

**Supported Providers:** Deepgram, AssemblyAI, Azure Speech, Google Cloud Speech

**Critical Details:**
- Use WebSocket for bidirectional streaming
- Run sender and receiver tasks with `asyncio.gather()`
- **Mute transcriber when bot speaks** — prevents echo/feedback loops

---

### 2. Agent (Text → Response)

```python
class BaseAgent:
    def __init__(self, agent_config):
        self.input_queue = asyncio.Queue()   # TranscriptionAgentInput
        self.output_queue = asyncio.Queue()  # AgentResponse
        self.transcript = None

    async def generate_response(self, human_input, is_interrupt, conversation_id):
        """Override — returns AsyncGenerator of response chunks."""
        raise NotImplementedError
```

**Why Streaming?** Lower latency, better interrupts, more natural flow.

**Critical Details:**
- Maintain conversation history in `Transcript` object
- Stream responses using `AsyncGenerator`
- **Buffer full sentences before yielding to synthesizer** — prevents audio jumping
- Handle interrupts by canceling current generation task

---

### 3. WebSocket Integration

```python
@app.websocket("/conversation")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    transcriber = voice_handler.create_transcriber(agent_config)
    agent = voice_handler.create_agent(agent_config)
    synthesizer = voice_handler.create_synthesizer(agent_config)

    output_device = WebsocketOutputDevice(
        ws=websocket,
        sampling_rate=16000,
        audio_encoding=AudioEncoding.LINEAR16
    )

    conversation = StreamingConversation(
        output_device=output_device,
        transcriber=transcriber,
        agent=agent,
        synthesizer=synthesizer
    )
    await conversation.start()

    try:
        async for message in websocket.iter_bytes():
            conversation.receive_audio(message)
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    finally:
        await conversation.terminate()
```

---

## Key Design Patterns

### Streaming Generators (Critical for Latency)
```python
# ❌ Bad: Wait for entire response
async def generate_response(prompt):
    response = await openai.complete(prompt)  # 5 seconds
    return response

# ✅ Good: Stream chunks as they arrive
async def generate_response(prompt):
    async for chunk in openai.complete(prompt, stream=True):
        yield chunk  # Yield after 0.1s, 0.2s, etc.
```

### Conversation State Management
```python
class Transcript:
    event_logs: List[Message] = []

    def add_human_message(self, text):
        self.event_logs.append(Message(sender=Sender.HUMAN, text=text))

    def add_bot_message(self, text):
        self.event_logs.append(Message(sender=Sender.BOT, text=text))

    def to_openai_messages(self):
        return [
            {"role": "user" if msg.sender == Sender.HUMAN else "assistant",
             "content": msg.text}
            for msg in self.event_logs
        ]
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Audio jumping/cutting off | Buffer entire LLM sentence before sending to TTS |
| Echo/feedback loop | Mute transcriber while bot speaks |
| Interrupts not working | Check VAD threshold; clear audio queue on interrupt |
| Memory leaks | Always `await conversation.terminate()` on disconnect |

---

## Implementation Order
1. Base Workers → Transcriber → Agent → Synthesizer
2. Wire with queues → Add interrupt system → Add WebSocket
3. Unit test each worker → Integration test full pipeline
4. Add error handling, rate limiting, monitoring

## Resources
- **asyncio**, **websockets**, **FastAPI** (WebSocket server)
- **pydub** — Audio manipulation
- **Transcription**: Deepgram, AssemblyAI, Azure Speech, Google Cloud Speech
- **LLM**: OpenAI, Google Gemini, Anthropic Claude
- **TTS**: ElevenLabs, Azure TTS, Google Cloud TTS, Amazon Polly

## Summary
> Everything must **stream** and everything must be **interruptible** for natural, real-time conversations.
