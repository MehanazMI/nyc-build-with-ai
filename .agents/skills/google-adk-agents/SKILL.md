---
name: google-adk-agents
description: Build production-grade AI agents using Google Agent Development Kit (ADK), including multi-agent orchestration, MCP tool servers, A2A protocol, Gemini Live API, Kafka messaging, and Cloud Spanner property graphs. Learned from completing the Way Back Home hackathon project (Levels 0–5).
---

# Google ADK Agent Development Skill

Comprehensive guide for building AI agent systems with Google ADK, grounded in real implementation experience across 6 production-grade projects.

---

## Environment Setup

### Installation
```bash
# Always use uv for dependency management
python -m uv sync

# Key packages
pip install google-adk google-genai a2a-sdk fastmcp aiokafka sse-starlette
```

### Required Environment Variables
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_GENAI_USE_VERTEXAI="true"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

### Windows Gotcha — gcloud + Python 3.14
```powershell
# gcloud breaks on Python 3.14 — point it to 3.11
$env:CLOUDSDK_PYTHON = "C:\path\to\python3.11.exe"
```

---

## Pattern 1: Basic ADK Agent

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="MyAgent",
    model="gemini-2.5-flash",
    instruction="You are a helpful agent. {user_name} is waiting for your response.",
    tools=[my_tool],
)
```

> **Key**: Use `{key}` placeholders in instructions — NOT f-strings. The ADK engine resolves these at runtime from session state.

---

## Pattern 2: before_agent_callback — Pre-flight State Setup

Run setup code ONCE before the agent handles any request. Use this to fetch config, user data, API responses.

```python
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents import Agent

async def setup_context(ctx: CallbackContext) -> None:
    """Fetch participant data and populate state for all sub-agents."""
    import httpx
    async with httpx.AsyncClient() as client:
        data = (await client.get(f"{BACKEND_URL}/participants/{PARTICIPANT_ID}")).json()
    
    ctx.state["username"] = data["username"]
    ctx.state["evidence_url"] = data["evidence_urls"]["soil"]
    ctx.state["project_id"] = os.environ["GOOGLE_CLOUD_PROJECT"]

root_agent = Agent(
    name="RootAgent",
    before_agent_callback=setup_context,
    instruction="Analyze evidence for {username}. Evidence: {evidence_url}",
    ...
)
```

> All sub-agents automatically inherit state set by the root callback. No need to pass explicitly.

---

## Pattern 3: ParallelAgent — Run Specialists Concurrently

```python
from google.adk.agents import ParallelAgent, Agent

geological = Agent(name="GeologicalAnalyst", tools=[geological_mcp_tool], ...)
botanical = Agent(name="BotanicalAnalyst", tools=[botanical_mcp_tool], ...)
astronomical = Agent(name="AstronomicalAnalyst", tools=[bigquery_mcp_tool], ...)

crew = ParallelAgent(
    name="AnalysisCrew",
    sub_agents=[geological, botanical, astronomical],
)
# ~10s parallel vs ~30s sequential
```

> ⚠️ **Critical**: Each parallel sub-agent needs its **own** `MCPToolset` instance. Never share a singleton — they'll conflict.

---

## Pattern 4: SequentialAgent — Pipeline

```python
from google.adk.agents import SequentialAgent

pipeline = SequentialAgent(
    name="MultimediaPipeline",
    sub_agents=[upload_agent, extraction_agent, spanner_save_agent, summary_agent],
)
# Output of each step flows to next step via session state
```

---

## Pattern 5: ToolContext — Read State in Tools

```python
from google.adk.tools import ToolContext

def activate_beacon(biome: str, tool_context: ToolContext) -> dict:
    pid = tool_context.state["participant_id"]
    # ✅ Never import config files in tools — read from state
    ...
```

---

## Pattern 6: Custom MCP Server (FastMCP)

### Server
```python
# mcp_server/main.py
from fastmcp import FastMCP
import google.generativeai as genai

mcp = FastMCP("location-analyzer")

@mcp.tool()
def analyze_geological(image_url: str) -> dict:
    """Analyze soil/mineral sample to classify biome."""
    client = genai.GenerativeModel("gemini-2.5-flash")
    response = client.generate_content([
        "Analyze this geological sample and classify the biome. Return JSON.",
        {"url": image_url}
    ])
    return json.loads(response.text)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)
```

### Client (in ADK agent)
```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

geo_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"{os.getenv('MCP_SERVER_URL')}/mcp"
    )
)

agent = Agent(name="GeologicalAnalyst", tools=[geo_toolset], ...)
```

### Deploy MCP Server to Cloud Run
```bash
# cloudbuild.yaml in mcp_server/
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions="_SERVICE_ACCOUNT=my-sa@project.iam.gserviceaccount.com" \
  --project=my-project
```

---

## Pattern 7: Google Cloud MCP (Managed — BigQuery)

```python
import google.auth
import google.auth.transport.requests

def get_token() -> str:
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token

bq_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://bigquery.googleapis.com/mcp",
        headers={"Authorization": f"Bearer {get_token()}"}
    )
)
```

---

## Pattern 8: A2A Protocol (RemoteA2aAgent)

```python
from google.adk.agents.remote_agent import RemoteA2aAgent

# Treat a remote A2A-compliant HTTP server as a local sub-agent
remote_agent = RemoteA2aAgent(
    name="ArchitectAgent",
    agent_url="http://localhost:8081",  # must serve /.well-known/agent.json
)

dispatcher = Agent(
    name="DispatchAgent",
    sub_agents=[remote_agent],
    ...
)
```

### Start an A2A-compatible Server
```bash
uvicorn server:app --host 0.0.0.0 --port 8081
# server.py uses A2AFastAPIApp or similar from a2a-sdk
```

> The `a2a-sdk` server must expose `GET /.well-known/agent.json` with the agent card.

---

## Pattern 9: Gemini Live API — Real-time Audio/Video

```python
from google.adk.runners import Runner
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.genai import types

# Create a queue for upstream audio/video frames
queue = LiveRequestQueue()

# Feed frames upstream (from WebSocket)
async def upstream_task(ws, queue):
    async for data in ws.iter_bytes():
        blob = types.Blob(data=data, mime_type="audio/pcm;rate=16000")
        queue.send_realtime(blob)

# Stream Gemini responses downstream (to WebSocket)
async def downstream_task(ws, runner, session):
    async for event in runner.run_live(
        user_id="user",
        session_id=session.id,
        live_request_queue=queue,
    ):
        if event.server_content and event.server_content.model_turn:
            for part in event.server_content.model_turn.parts:
                if part.inline_data:
                    await ws.send_bytes(part.inline_data.data)
```

### Gemini Live Agent Config
```python
from google.genai import types

agent = Agent(
    name="LiveAgent",
    model="gemini-live-2.5-flash-preview-native-audio",
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
            )
        ),
        system_instruction="You are an assistant. Call report_digit() when you see fingers.",
    ),
    tools=[report_digit_tool],
)
```

---

## Pattern 10: Kafka A2A Bridge (aiokafka)

> ⚠️ **`a2a.server.apps.kafka` and `a2a.client.transports.kafka` DO NOT EXIST in any public PyPI release of `a2a-sdk`** (as of 2026-03). Implement the bridge directly with `aiokafka`.

### Formation Agent (Kafka Consumer → ADK Runner)
```python
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio, json, uuid
from google.adk.runners import Runner

class KafkaServerApp:
    def __init__(self, agent, bootstrap_servers, request_topic, reply_topic):
        self.agent = agent
        self.bootstrap_servers = bootstrap_servers
        self.request_topic = request_topic
        self.reply_topic = reply_topic

    async def run(self):
        consumer = AIOKafkaConsumer(
            self.request_topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id="agent-group",
            auto_offset_reset="latest",
        )
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        await consumer.start(); await producer.start()

        async for msg in consumer:
            request = json.loads(msg.value)
            response_text = await self._run_agent(request["text"])
            reply = {"message_id": request["message_id"], "text": response_text}
            await producer.send_and_wait(
                request["reply_topic"],
                json.dumps(reply).encode()
            )
```

### Satellite (Request-Reply with asyncio.Future)
```python
pending_replies: dict[str, asyncio.Future] = {}

# Send request
async def send_formation_request(text: str) -> str:
    msg_id = str(uuid.uuid4())
    future = asyncio.get_event_loop().create_future()
    pending_replies[msg_id] = future  # register BEFORE sending

    await producer.send_and_wait(
        "a2a-request-topic",
        json.dumps({"message_id": msg_id, "reply_topic": REPLY_TOPIC, "text": text}).encode()
    )
    return await asyncio.wait_for(future, timeout=120.0)

# Reply consumer (background task)
async def reply_consumer():
    async for msg in consumer:
        reply = json.loads(msg.value)
        future = pending_replies.pop(reply["message_id"], None)
        if future and not future.done():
            future.set_result(reply)
```

---

## Pattern 11: SSE Streaming (FastAPI)

```python
from sse_starlette.sse import EventSourceResponse
import asyncio, json

@app.get("/stream")
async def stream(request: Request):
    async def generator():
        while True:
            if await request.is_disconnected():
                break
            for pod in pods:
                yield {"event": "pod_update", "data": json.dumps({"pod": pod})}
                await asyncio.sleep(0.02)
            await asyncio.sleep(0.5)
    return EventSourceResponse(generator())
```

---

## Pattern 12: Cloud Spanner Property Graph

```python
# Schema creation
CREATE PROPERTY GRAPH SurvivorGraph
  NODE TABLES (survivors, skills, needs)
  EDGE TABLES (
    survivor_skills SOURCE KEY (survivor_id) REFERENCES survivors
                    DESTINATION KEY (skill_id) REFERENCES skills
  );

# GQL Query
GRAPH SurvivorGraph
MATCH (s:Survivor)-[:HAS_SKILL]->(skill:Skill {name: 'Python'})
RETURN s.name, s.location
LIMIT 10
```

> Requires **ENTERPRISE** or higher Spanner edition.
> Use `ML.PREDICT` for inline embedding + semantic search.

---

## Gemini Image Generation (Multi-turn Chat)

```python
from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project=PROJECT, location="us-central1")

chat = client.chats.create(
    model="gemini-2.5-flash-image",
    config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
)

# Turn 1: portrait
response = chat.send_message([prompt_text, types.Part.from_bytes(photo_bytes, "image/jpeg")])

# Turn 2: icon (chat session "remembers" the character)
icon_response = chat.send_message("Create a small badge icon of this same character.")

# Extract image
for part in response.candidates[0].content.parts:
    if part.inline_data:
        img = Image.open(io.BytesIO(part.inline_data.data))
```

---

## Docker + Kafka (Local Development)

```bash
# Start Kafka (KRaft mode — no ZooKeeper)
CLUSTER_ID=$(docker run --rm apache/kafka:4.2.0-rc1 /opt/kafka/bin/kafka-storage.sh random-uuid)
docker run -d --name mission-kafka -p 9092:9092 \
  -e CLUSTER_ID=$CLUSTER_ID \
  -e KAFKA_PROCESS_ROLES=broker,controller \
  -e KAFKA_NODE_ID=1 \
  -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -e KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://127.0.0.1:9092 \
  -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@127.0.0.1:9093 \
  -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  apache/kafka:4.2.0-rc1
```

---

## Common Gotchas

| Gotcha | Fix |
|--------|-----|
| `a2a.server.apps.kafka` import fails | Doesn't exist publicly — use `aiokafka` directly |
| Parallel agents conflict on MCPToolset | Give each its own `MCPToolset()` instance |
| `{key}` shows as literal in response | State wasn't populated — check callback ran |
| `before_agent_callback` doesn't fire | Must be `async def` matching the ADK signature |
| Gemini Live disconnects immediately | Check `response_modalities` includes `"AUDIO"` |
| `uv pip install` targets system Python | Add `--python .venv/Scripts/python.exe` |
| `pydantic` version conflict | Use `pydantic>=2.11` (not pinned to minor) |
| Port 8000 ghost process (Windows) | Change port to 8082/8083/etc. |
| `gcloud` fails on Python 3.14 | `$env:CLOUDSDK_PYTHON = "python3.11"` |
| uvicorn `CancelledError` on shutdown | Python 3.14 asyncio behavior — not a real error |
| Avatar API requires both portrait + icon | `POST /avatar` needs `{portrait, icon}` multipart fields |
| `RemoteA2aAgent` can't find agent card | Server must expose `GET /.well-known/agent.json` |

---

## Running Service Stack

```powershell
# Level 5 full stack (run each in its own terminal)

# 1. Kafka
docker start mission-kafka

# 2. Formation Agent
$env:GOOGLE_GENAI_USE_VERTEXAI = "true"
$env:GOOGLE_CLOUD_PROJECT = "ai-hack-489018"
$env:KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
python -m agent.server

# 3. Satellite Dashboard
$env:KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
uvicorn satellite.main:app --host 0.0.0.0 --port 8083
```

---

## References

- [ADK Docs](https://google.github.io/adk-docs/) — Agent Development Kit
- [ADK Callbacks](https://google.github.io/adk-docs/callbacks/) — before/after agent/tool callbacks
- [A2A Python SDK](https://google-a2a.github.io/a2a-python/) — Agent-to-Agent Protocol
- [FastMCP](https://gofastmcp.com) — MCP server framework
- [aiokafka](https://aiokafka.readthedocs.io/) — Async Kafka client
- [Google GenAI SDK](https://googleapis.github.io/python-genai/) — Gemini API
- [Cloud Spanner Property Graphs](https://cloud.google.com/spanner/docs/property-graphs-overview)
