# AGENTS.md

> Guidance for AI coding agents working on the **Way Back Home** project.
> Explorer: ExplorerMz | Participant: `ee34c542` | Event: `sandbox` | Project: `ai-hack-489018`

---

## ⚠️ Critical: Repository Structure

This repo has two parallel folder systems — **do not confuse them**:

| Folder | What it is | What to do |
|--------|-----------|------------|
| `level_0/`, `level_1/`, `level_2/` ... | **Starter code** with `#REPLACE` placeholders | ✅ **Edit these** — implement the placeholders |
| `solutions/level_0/`, `solutions/level_1/` ... | **Complete reference implementations** | 🔍 **Read-only** — use as reference when stuck |

**Workflow:**
1. Work in `level_X/` — find `#REPLACE` or `#TODO` comments and implement them
2. If stuck on what to implement, read the corresponding file in `solutions/level_X/`
3. Never copy-paste blindly from solutions — understand *why* before implementing
4. The `solutions/` folder came from the upstream workshop repo and should never be committed to

---

## Project Overview

Way Back Home is a multi-level Google Cloud AI hackathon project. A space explorer (ExplorerMz) has crashed on an alien planet and must use AI agents to get rescued.

```
level_0/   → Avatar generation (Gemini multi-turn image generation)
level_1/   → Crash site analysis (ADK multi-agent + MCP servers)
level_2/   → Survivor network (Cloud Spanner graph + Vertex AI)
level_3/   → SOS signal processing (Gemini Live API, real-time audio)
level_4/   → Rescue dispatch (A2A protocol, Redis, multi-agent)
level_5/   → Group rescue coordination (Kafka + aiokafka A2A bridge)
solutions/ → Reference implementations for each level
PLAN.md    → High-level progress tracker
DEVLOG.md  → Step-by-step implementation notes
```

---

## Setup

### Prerequisites
- Python 3.11+ with `.venv` per level (managed by `uv`)
- Google Cloud SDK (`gcloud`) authenticated
- GCP Project: `ai-hack-489018`, Region: `us-central1`
- Service Account: `way-back-home-sa@ai-hack-489018.iam.gserviceaccount.com`
- Docker Desktop (for Level 5 Kafka)

### Per-level venv (uv)
```bash
cd way-back-home/level_X
python -m uv sync        # installs from pyproject.toml
# activate:
.venv/Scripts/activate   # Windows
source .venv/bin/activate  # Mac/Linux
```

### Required Environment Variables
```bash
export GOOGLE_CLOUD_PROJECT="ai-hack-489018"
export GOOGLE_GENAI_USE_VERTEXAI="true"
export GOOGLE_CLOUD_LOCATION="us-central1"
export PARTICIPANT_ID="ee34c542"
export BACKEND_URL="https://api.waybackhome.dev"
```

### Windows Gotcha — `gcloud` + Python 3.14
```powershell
# gcloud uses system Python; if 3.14 is default it may break.
$env:CLOUDSDK_PYTHON = "C:\path\to\python3.11.exe"
```

---

## Architecture — All Levels

### Level 0: Avatar Generation
```
Gemini chat session (multi-turn)
  Turn 1: photo + portrait_prompt → portrait.png (preserve face likeness)
  Turn 2: icon_prompt → icon.png (consistent circular badge)
Upload: POST /participants/{id}/avatar with {portrait, icon} fields
```

### Level 1: Crash Site Analysis (ADK)
```
before_agent_callback → fetch participant data → populate state
MissionAnalysisAI (Root)
└── EvidenceAnalysisCrew (ParallelAgent)
    ├── GeologicalAnalyst  → Custom MCP (Cloud Run) → analyze_geological()
    ├── BotanicalAnalyst   → Custom MCP (Cloud Run) → analyze_botanical()
    └── AstronomicalAnalyst → BigQuery MCP → execute_query()
→ confirm_location tool → PATCH /participants/{id}/location
```

### Level 2: Survivor Network (Graph + RAG)
```
FastAPI Backend (:8000)
├── survivor_network_agent (ADK Agent)
│   └── hybrid_search, semantic_search, find_similar_skills, get_urgent_needs
├── HybridSearchService → Cloud Spanner (keyword + ML.PREDICT embeddings)
├── GraphService → Cloud Spanner Property Graph (GQL)
├── MultimediaExtractionPipeline (SequentialAgent → upload → extract → save)
└── GCSService → Cloud Storage
React Frontend (:5173) — 3D graph visualization + AI chat
```

### Level 3: SOS Signals (Gemini Live API)
```
Browser (cam + mic) ──WebSocket──► FastAPI (:8080)
                                    ├── upstream: WS frames → LiveRequestQueue
                                    ├── downstream: runner.run_live() → WS
                                    └── BiometricAgent
                                         ├── model: gemini-live-2.5-flash-preview-native-audio
                                         └── tool: report_digit(count)
```

### Level 4: Dispatch Agent (A2A)
```
Browser ──WebSocket──► Dispatch Agent (:8082, Gemini Live)
                            ├── monitor_for_hazard (video analysis)
                            ├── lookup_schematic_tool → Redis (:6379)
                            └── RemoteA2aAgent → Architect Agent (:8081, A2A)
                                                   └── lookup_schematic_tool → Redis
```

### Level 5: Group Rescue (Kafka A2A)
```
React Frontend (SSE) ←→ Satellite Dashboard (:8083)
                                ↕ aiokafka Producer/Consumer
                         Kafka Broker (:9092)
                         topics: a2a-formation-request, a2a-reply-satellite-dashboard
                                ↕
                         Formation Agent (KafkaServerApp shim)
                                ↕
                         Gemini 2.5 Flash → 15 XY pod coordinates
```

---

## Key ADK Patterns (Learned Across All Levels)

### 1. `before_agent_callback` — Pre-flight State Setup
```python
async def setup_context(ctx: CallbackContext) -> None:
    data = await api_client.get(f"/participants/{participant_id}")
    ctx.state["soil_url"] = data["evidence_urls"]["soil"]
    ctx.state["username"] = data["username"]

root_agent = Agent(before_agent_callback=setup_context, ...)
```
> ONE API call at startup, all sub-agents get state for free.

### 2. `{key}` State Templating — Never F-Strings in Instructions
```python
agent = Agent(
    instruction="Analyze this URL: {soil_url}",  # ✅ resolved at runtime
    # NOT: f"Analyze this URL: {soil_url}"       # ❌ fails — state not set yet
)
```

### 3. `ToolContext` — Reading State Inside Tools
```python
def confirm_location(biome: str, tool_context: ToolContext) -> dict:
    pid = tool_context.state["participant_id"]  # ✅ read from session state
```

### 4. `ParallelAgent` — Concurrent Independent Tasks
```python
crew = ParallelAgent(
    name="EvidenceAnalysisCrew",
    sub_agents=[geological_analyst, botanical_analyst, astronomical_analyst],
)
# ~10s parallel vs ~30s sequential — always use for independent analyses
```
> ⚠️ Each parallel agent needs its **own** `MCPToolset` instance — never share one singleton.

### 5. `SequentialAgent` — Pipeline Pattern
```python
pipeline = SequentialAgent(
    name="MultimediaPipeline",
    sub_agents=[upload_agent, extraction_agent, save_agent, summary_agent],
)
```

### 6. `RemoteA2aAgent` — A2A Protocol (Level 4)
```python
from google.adk.agents.remote_agent import RemoteA2aAgent

architect_agent = RemoteA2aAgent(
    name="ArchitectAgent",
    agent_url="http://localhost:8081",
)
# Plug in as a sub-agent — parent treats it like any local agent
```

### 7. `Runner.run_live()` — Gemini Live API (Level 3)
```python
async for event in runner.run_live(
    user_id="user",
    session_id=session.id,
    live_request_queue=queue,
):
    if event.server_content and event.server_content.model_turn:
        for part in event.server_content.model_turn.parts:
            if part.inline_data:
                await websocket.send_bytes(part.inline_data.data)
```

### 8. Kafka A2A (Level 5) — `a2a.server.apps.kafka` DOES NOT EXIST PUBLICLY
```python
# ❌ These imports fail — not in any public PyPI release of a2a-sdk:
from a2a.server.apps.kafka import KafkaServerApp
from a2a.client.transports.kafka import KafkaClientTransport

# ✅ Implement directly with aiokafka:
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

consumer = AIOKafkaConsumer(topic, bootstrap_servers=bootstrap_servers)
producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
```
> Use `asyncio.Future` dict for request-reply correlation between producer (satellite) and consumer (agent).

### 9. SSE Streaming — Real-time Frontend Updates
```python
from sse_starlette.sse import EventSourceResponse

@app.get("/stream")
async def stream(request: Request):
    async def generator():
        while True:
            yield {"event": "pod_update", "data": json.dumps(pod)}
            await asyncio.sleep(0.5)
    return EventSourceResponse(generator())
```

---

## MCP Tool Patterns

### Custom MCP — FastMCP on Cloud Run
```python
# server: level_1/mcp-server/main.py
from fastmcp import FastMCP
mcp = FastMCP("location-analyzer")

@mcp.tool()
def analyze_geological(image_url: str) -> dict:
    # Gemini Vision analysis
    ...

# client: agent/tools/mcp_tools.py
MCPToolset(connection_params=StreamableHTTPConnectionParams(url=f"{MCP_URL}/mcp"))
```

### Google Cloud MCP (Managed)
```python
MCPToolset(connection_params=StreamableHTTPConnectionParams(
    url="https://bigquery.googleapis.com/mcp",
    headers={"Authorization": f"Bearer {token}"}
))
```

---

## Gemini Live API — Key Points (Level 3)

| Setting | Value |
|---------|-------|
| Model | `gemini-live-2.5-flash-preview-native-audio` |
| Config | `response_modalities=["AUDIO"]`, `speech_config` |
| Input | `LiveRequestQueue` — async queue for upstream frames |
| Output | `runner.run_live()` generator — yields `LiveEvent` |
| Audio format | `audio/pcm;rate=16000` upstream, `audio/pcm;rate=24000` downstream |

---

## A2A Protocol — Key Points (Level 4)

- Agents expose HTTP endpoints (`/.well-known/agent.json` + `/`) discovered by clients
- `RemoteA2aAgent` is a drop-in that wraps any A2A-compliant HTTP endpoint as a sub-agent
- Start server with: `uvicorn server:app --port 8081`
- The agent card (at `/.well-known/agent.json`) describes the agent's capabilities

---

## Cloud Spanner Property Graph (Level 2)

```sql
-- GQL query example
GRAPH SurvivorGraph
MATCH (s:Survivor)-[:HAS_SKILL]->(skill:Skill)
WHERE skill.name = 'Python'
RETURN s.name, s.location
```

- Property Graph requires `ENTERPRISE` or higher Spanner edition
- Schema: Survivors, Skills, Needs, Resources, Biomes as node tables; edges as interleaved tables
- RAG: `ML.PREDICT` model in Spanner applies embedding model + cosine similarity inline

---

## Sandbox API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/participants/{id}` | GET | Get participant state |
| `/participants/{id}` | PATCH | Update fields (`level_N_complete`, `completion_percentage`, etc.) |
| `/participants/{id}/avatar` | POST | Upload portrait + icon (both required as multipart) |
| `/participants/{id}/location` | PATCH | Activate beacon with biome |

> **Avatar upload requires BOTH `portrait` and `icon` fields** in a single multipart POST.

---

## Common Gotchas

| Gotcha | Fix |
|--------|-----|
| `ParallelAgent` MCPToolset shared | Give each agent its own MCPToolset instance |
| `{key}` in instructions showing raw | State wasn't set — check `before_agent_callback` ran |
| `a2a.server.apps.kafka` import fails | Doesn't exist in public a2a-sdk — use aiokafka directly |
| `a2a-sdk[kafka]` extra not found (0.3.24) | The kafka extra doesn't exist in any PyPI release |
| `gcloud` fails on Python 3.14 | Set `$env:CLOUDSDK_PYTHON` to 3.11 binary |
| Port 8000 ghost process (Windows) | Use a different port (8082, 8083, etc.) |
| uvicorn `CancelledError` on shutdown | Python 3.14 asyncio quirk — not a real error |
| `uv pip install` targets system Python | Use `--python .venv/Scripts/python.exe` flag |
| `pydantic` version conflict | Use `pydantic>=2.11` (not pinned to minor) |
| Frontend SSE not receiving | Check CORS — must allow `localhost` origin |

---

## After Completing Each Level

- [ ] Update `PLAN.md` — mark level ✅, add architecture summary
- [ ] Update `DEVLOG.md` — step-by-step with commands, files changed, verification
- [ ] Patch sandbox: `PATCH /participants/{id}` → `{"level_N_complete": true, "completion_percentage": 100}`
- [ ] Upload avatar: `POST /participants/{id}/avatar` with portrait + icon files
- [ ] `git add && git commit && git push`

---

## GCP Resources

| Resource | Value |
|----------|-------|
| Project | `ai-hack-489018` |
| Region | `us-central1` |
| MCP Server (Cloud Run) | `https://location-analyzer-avamvnovja-uc.a.run.app` |
| BigQuery dataset | `ai-hack-489018.way_back_home.star_catalog` |
| Spanner Instance | `survivor-network` (ENTERPRISE) |
| Spanner Database | `graph-db` / Graph: `SurvivorGraph` |
| GCS Bucket | `gs://survivor-network-media-ai-hack-489018` |
| Artifact Registry | `us-central1-docker.pkg.dev/ai-hack-489018/way-back-home` |
| Service Account | `way-back-home-sa@ai-hack-489018.iam.gserviceaccount.com` |

---

## Reference

- [PLAN.md](PLAN.md) — Level-by-level progress
- [DEVLOG.md](DEVLOG.md) — Step-by-step implementation notes
- [solutions/](solutions/) — Reference implementations for each level
- [ADK Docs](https://google.github.io/adk-docs/) — Agent Development Kit
- [A2A Protocol](https://google-a2a.github.io/a2a-python/) — Agent-to-Agent SDK
- [FastMCP Docs](https://gofastmcp.com) — MCP server framework
- [aiokafka Docs](https://aiokafka.readthedocs.io/) — Async Kafka Python client
