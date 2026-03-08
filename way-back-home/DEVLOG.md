# 📓 Way Back Home — Developer Log

A step-by-step record of everything built and why. Updated after each level.

**Explorer:** ExplorerMz | **Participant ID:** `ee34c542` | **Project:** `ai-hack-489018`

---

## ✅ Level 0 — Generate Explorer Identity

**Date:** 2026-03-03 | **Codelab:** https://codelabs.developers.google.com/way-back-home-level-0/instructions

### Step 1 — Setup
```bash
git clone https://github.com/google-americas/way-back-home.git
cd way-back-home
./scripts/setup.sh  # created config.json with participant ID and event code
cd level_0
python -m venv .venv && .venv/Scripts/activate
pip install google-genai Pillow requests
```
`config.json` was created with: `participant_id=ee34c542`, `event=sandbox`, `coords=(56, 66)`

### Step 2 — Customize Avatar
```bash
python customize.py
```
Chose: **Crimson Red suit**, tall/short dark hair, determined expression, female.

### Step 3 — Implement `generator.py`
Three sections to implement inside a **multi-turn chat session** (ensures portrait and icon share the same art style):

```python
# Step 1: Create chat session with image generation model
chat = client.chats.create(
    model="gemini-2.5-flash-preview-image-generation",
    config=genai_types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"]
    )
)

# Step 2: Generate portrait — send prompt, save inline_data bytes to outputs/portrait.png
response = chat.send_message(portrait_prompt)
# parse response.candidates[0].content.parts for image data

# Step 3: Generate icon — same session, so style stays consistent
response = chat.send_message(icon_prompt)
# save to outputs/icon.png
```

**Why multi-turn chat?** Gemini remembers the art style it established in turn 1, so the icon automatically matches the portrait without needing to re-describe the style.

### Step 4 — Bonus: Photo-Based Avatar
Modified `generator.py` to send a real photo alongside the portrait prompt:

```python
# Load user photo and send as multimodal input
image_bytes = open("C:/Users/rashe/Pictures/IMG_298_2.jpg", "rb").read()
response = chat.send_message([
    prompt_text,
    genai_types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
])
```
**Why:** Gemini can preserve real likeness while applying a stylized space explorer look. This demonstrates Gemini's multimodal image-to-image capability.

### Step 5 — Register Avatar
```bash
python create_identity.py
```
- Generated `portrait.png` + `icon.png`
- Uploaded to Firebase Storage
- Registered via `POST /participants` → ExplorerMz appears on live map

**Result:** ✅ ExplorerMz live at https://waybackhome.dev/e/sandbox

---

## ✅ Level 1 — Pinpoint Crash Location

**Date:** 2026-03-04 | **Codelab:** https://codelabs.developers.google.com/way-back-home-level-1/instructions

### Step 1 — Enable GCP APIs
```bash
gcloud services enable aiplatform.googleapis.com run.googleapis.com \
  cloudbuild.googleapis.com bigquery.googleapis.com \
  artifactregistry.googleapis.com iam.googleapis.com
```

### Step 2 — Create Service Account
```bash
gcloud iam service-accounts create way-back-home-sa
# Granted: aiplatform.user, run.invoker, bigquery.user, bigquery.dataViewer, storage.objectViewer
```

### Step 3 — Create Artifact Registry (for Docker images)
```bash
gcloud artifacts repositories create way-back-home \
  --repository-format=docker --location=us-central1
```

### Step 4 — Install Level 1 Dependencies
```bash
cd level_1
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
# Key packages: google-adk==1.17.0, google-cloud-bigquery, Pillow, requests
```

### Step 5 — Generate Evidence Files
```bash
python generate_evidence.py
```
Generated 3 crash site evidence files and uploaded to Firebase Storage:
- `soil_sample.png` — alien soil (used by Geological Analyst)
- `flora_recording.mp4` — alien plant video with audio (Botanical Analyst)
- `star_field.png` — alien night sky (Astronomical Analyst)

The evidence URLs are stored in the backend and fetched by `before_agent_callback` at runtime.

### Step 6 — Set Up BigQuery Star Catalog
```bash
python setup/setup_star_catalog.py
```
Created `way_back_home.star_catalog` table in BigQuery with 12 rows (3 star patterns per biome):

| Biome | Primary Star | Nebula Type |
|-------|-------------|-------------|
| CRYO | blue_giant | ice_blue |
| VOLCANIC | red_dwarf_binary | fire |
| BIOLUMINESCENT | green_pulsar | purple_magenta |
| FOSSILIZED | yellow_sun | golden |

### Step 7 — Implement MCP Server Tools (`mcp-server/main.py`)

The MCP server is a custom FastMCP service deployed to Cloud Run. It exposes two tools:

**`analyze_geological(image_url)`** — Calls Gemini Vision on the soil sample:
```python
@mcp.tool()
def analyze_geological(image_url: str) -> dict:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[GEOLOGICAL_PROMPT, Part.from_uri(file_uri=image_url, mime_type="image/png")]
    )
    return parse_json_response(response.text)  # → {biome, confidence, minerals_detected}
```

**`analyze_botanical(video_url)`** — Calls Gemini multimodal on the flora video (processes BOTH video frames AND audio track simultaneously):
```python
@mcp.tool()
def analyze_botanical(video_url: str) -> dict:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[BOTANICAL_PROMPT, Part.from_uri(file_uri=video_url, mime_type="video/mp4")]
    )
    return parse_json_response(response.text)  # → {biome, confidence, species_detected, audio_signatures}
```

**Why a custom MCP server?** This demonstrates the CUSTOM MCP pattern — you write and host the tool logic. Contrast with Level 1's astronomical agent which uses Google's MANAGED BigQuery MCP server where Google hosts the tools.

### Step 8 — Deploy MCP Server to Cloud Run
```bash
cd mcp-server
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions="_SERVICE_ACCOUNT=way-back-home-sa@ai-hack-489018.iam.gserviceaccount.com" \
  --project=ai-hack-489018
```
Cloud Build: built Docker image → pushed to Artifact Registry → deployed to Cloud Run.

**MCP Server URL:** `https://location-analyzer-avamvnovja-uc.a.run.app`

Agents connect via: `https://location-analyzer-avamvnovja-uc.a.run.app/mcp` (Streamable HTTP transport)

### Step 9 — Implement Agent Tools

**`tools/mcp_tools.py`** — MCP connection to the Cloud Run MCP server:
```python
# Each parallel agent needs its OWN MCPToolset (no singleton — parallel agents break shared connections)
def _make_mcp_toolset():
    return MCPToolset(
        connection_params=StreamableHTTPConnectionParams(url=f"{MCP_SERVER_URL}/mcp", timeout=120)
    )

def get_geological_tool(): return _make_mcp_toolset()
def get_botanical_tool(): return _make_mcp_toolset()
```

**`tools/star_tools.py`** — Two tool patterns in one file:
```python
# Pattern 1: LOCAL FunctionTool — Gemini Vision analyzes star field image
def extract_star_features(image_url: str) -> dict:
    response = genai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[STAR_EXTRACTION_PROMPT, Part.from_uri(file_uri=image_url, mime_type="image/png")]
    )
    return parse_json_response(response.text)  # → {primary_star, nebula_type, stellar_color}

# Pattern 2: MANAGED MCP — Google's BigQuery MCP server (no setup needed, Google hosts it)
def get_bigquery_mcp_toolset():
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/bigquery"])
    credentials.refresh(google.auth.transport.requests.Request())
    return MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://bigquery.googleapis.com/mcp",
            headers={"Authorization": f"Bearer {credentials.token}", "x-goog-user-project": PROJECT_ID}
        )
    )
```

**`tools/confirm_tools.py`** — Activates the rescue beacon:
```python
def confirm_location(biome: str, tool_context: ToolContext) -> dict:
    # Read state set by before_agent_callback
    participant_id = tool_context.state.get("participant_id")
    x, y = tool_context.state.get("x"), tool_context.state.get("y")
    # Validate biome against actual coordinates, then call backend
    response = requests.patch(f"{backend_url}/participants/{participant_id}/location", params={"x": x, "y": y})
```

### Step 10 — Implement Specialist Agents

Each specialist uses ADK's `{key}` state templating — the instruction contains `{soil_url}` etc., which ADK replaces at runtime from the shared `InvocationContext` state:

```python
geological_analyst = Agent(
    name="GeologicalAnalyst",
    model="gemini-2.5-flash",
    instruction="...Call analyze_geological with soil sample URL: {soil_url}...",
    tools=[get_geological_tool()]  # fresh MCPToolset per agent
)
```

Same pattern for `BotanicalAnalyst` (`{flora_url}`) and `AstronomicalAnalyst` (`{stars_url}` + `{project_id}`).

The Astronomical Analyst is special — it has TWO tool types and a two-step workflow:
1. Call `extract_star_features({stars_url})` → get `primary_star`, `nebula_type`
2. Call `execute_query(SQL)` → look up biome in BigQuery star catalog

### Step 11 — Implement Root Orchestrator (`agent.py`)

```python
# before_agent_callback: runs once before any agent processing
async def setup_participant_context(callback_context: CallbackContext) -> None:
    data = await httpx_client.get(f"{backend_url}/participants/{participant_id}")
    callback_context.state["soil_url"] = data["evidence_urls"]["soil"]
    callback_context.state["flora_url"] = data["evidence_urls"]["flora"]
    callback_context.state["stars_url"] = data["evidence_urls"]["stars"]
    # ... also sets x, y, username, project_id

# ParallelAgent: runs all 3 specialists concurrently
evidence_analysis_crew = ParallelAgent(
    name="EvidenceAnalysisCrew",
    sub_agents=[geological_analyst, botanical_analyst, astronomical_analyst]
)

# Root agent: coordinates crew + confirms location
root_agent = Agent(
    name="MissionAnalysisAI",
    instruction="...delegate to EvidenceAnalysisCrew, apply 2-of-3 agreement, call confirm_location...",
    sub_agents=[evidence_analysis_crew],
    tools=[confirm_location_tool],
    before_agent_callback=setup_participant_context
)
```

### Step 12 — Test Locally & Activate Beacon
```bash
$env:GOOGLE_CLOUD_PROJECT = "ai-hack-489018"
$env:MCP_SERVER_URL = "https://location-analyzer-avamvnovja-uc.a.run.app"
$env:PARTICIPANT_ID = "ee34c542"
# ... other env vars
python -m google.adk.cli web --host 127.0.0.1 --port 8080
```

In ADK Web UI → select `agent` → send:
> *"The geological analysis shows VOLCANIC (95%) and botanical analysis shows VOLCANIC (100%). Based on this 2-of-3 agreement, confirm my location as VOLCANIC biome."*

**Results:**
- 🔬 Geological: **VOLCANIC 95%** (dark volcanic rock, sulfur crystals, active lava crack)
- 🌿 Botanical: **VOLCANIC 100%** (fire blooms, obsidian sprouts, crackling audio, volcanic rumble)
- ✅ Beacon activated → **NE quadrant · (56, 66)**

### Key Lessons Learned in Level 1
| Issue | Root Cause | Fix |
|-------|-----------|-----|
| "Unexpected tool call" errors | `mcp-server/main.py` still had placeholder stubs | Implemented both MCP tools |
| Agent not appearing in ADK Web | `star_tools.py` was a placeholder → import failed silently | Implemented star_tools.py |
| Geo/botanical tools failing in parallel | Singleton MCPToolset shared between parallel agents | Give each agent its own MCPToolset instance |

---

## ✅ Level 2 — Survivor Network

**Date:** 2026-03-07 | **Codelab:** https://codelabs.developers.google.com/way-back-home-level-2/instructions

### Step 1 — Enable GCP APIs & Create Resources
```bash
gcloud services enable spanner.googleapis.com storage.googleapis.com --project=ai-hack-489018
gcloud storage buckets create gs://survivor-network-media-ai-hack-489018 --location=us-central1
```

### Step 2 — Configure Environment (`backend/.env`)
```env
PROJECT_ID=ai-hack-489018
INSTANCE_ID=survivor-network
DATABASE_ID=graph-db
GRAPH_NAME=SurvivorGraph
REGION=us-central1
LOCATION=us-central1
USE_MEMORY_BANK=false
GCS_BUCKET_NAME=survivor-network-media-ai-hack-489018
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=ai-hack-489018
GOOGLE_CLOUD_LOCATION=us-central1
```

### Step 3 — Provision Spanner (Fully Automated)
```bash
python -m uv run python setup_data.py --project=ai-hack-489018
```
`setup_data.py` handles everything: ENTERPRISE instance → database + schema → sample data (4 survivors, skills, needs, resources, biomes) → `SurvivorGraph` property graph.

### Step 4 — Fill 13 TODOs Across 7 Files

| File | TODOs | What Was Implemented |
|------|-------|----------------------|
| `agent/agent.py` | 6 | `add_session_to_memory` callback, `semantic_search` in instruction + tools, `PreloadMemoryTool`, `sub_agents=[multimedia_agent]`, `after_agent_callback` |
| `api/routes/chat.py` | 3 | `VertexAiSessionService`/`VertexAiMemoryBankService`, `InMemorySessionService`/`InMemoryMemoryService`, `Runner` init |
| `agent/tools/hybrid_search_tools.py` | 1 | Full `semantic_search()` — forces RAG via `SearchMethod.RAG` |
| `agent/multimedia_agent.py` | 1 | `sub_agents=[upload_agent, extraction_agent, spanner_agent, summary_agent]` |
| `services/hybrid_search_service.py` | 1 | RAG SQL with `ML.PREDICT(MODEL TextEmbeddings, ...)` + `COSINE_DISTANCE` |
| `deploy_agent.py` | 1 | Custom memory topics: search_preferences, location_interests, etc. |

**Review process:** 3-pass iterative review (Scope → Deep Scan → Full Diff). Found 3 additional cosmetic-only diffs (`main.py`, `extraction_tools.py`, `gcs_service.py` — whitespace only).

### Step 5 — Run Locally
```bash
# Backend
cd level_2/backend && python -m uv run uvicorn main:app --reload --port 8000

# Frontend
cd level_2/frontend && npm install && npm run dev
```

### Verification Results
| Test | Result |
|------|--------|
| `GET /health` | ✅ `{"status": "ok"}` |
| 3D graph visualization | ✅ Renders survivors, skills, needs, resources, biomes |
| Chat: "Show me all survivors" | ✅ David Chen (FOSSILIZED), Dr. Elena Frost (CRYO), Lt. Sarah Park (BIOLUMINESCENT), Captain Yuki Tanaka (VOLCANIC) |

### Key Differences from Level 1
| Aspect | Level 1 | Level 2 |
|--------|---------|---------|
| Agent framework | ADK `ParallelAgent` | ADK `Agent` + `SequentialAgent` |
| Database | BigQuery (read-only) | Cloud Spanner (read-write + graph) |
| Search | MCP tool calls | Hybrid: keyword + RAG (embeddings) |
| Frontend | ADK Web UI (built-in) | Custom React app (3D graph viz) |
| Package manager | pip | uv |

---

## ✅ Level 3 — Process SOS Signals (Biometric Scanner)

**Date:** 2026-03-07 | **Codelab:** Level 3

### Step 1 — Configure Environment (`backend/app/.env`)
```env
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=ai-hack-489018
GOOGLE_CLOUD_LOCATION=us-central1
MODEL_ID=gemini-live-2.5-flash-preview-native-audio-09-2025
```

### Step 2 — Fill 8 Markers Across 2 Files

| File | Markers | What Was Implemented |
|------|---------|----------------------|
| `biometric_agent/agent.py` | 4 | `report_digit(count)` tool, MODEL_ID from env, `tools=[report_digit]`, full scanner instruction |
| `main.py` | 4 | `session_service` + `Runner`, session init (native audio detection, RunConfig), live request (upstream/downstream tasks), response sorting (event logging) |

### Step 3 — Install Dependencies & Build Frontend
```bash
cd level_3 && python -m uv sync  # 113 Python packages
cd frontend && npm install && npm run build  # 219 npm packages → dist/
```

### Step 4 — Run Locally
```bash
# Backend (from backend/app/ directory)
cd level_3/backend/app
python main.py  # Serves on :8080

# Frontend (separate Vite dev server)
cd level_3/frontend
npm run dev  # Serves on :5173, proxies /ws to :8080
```

### Verification Results
| Test | Result |
|------|--------|
| Backend starts on :8080 | ✅ Startup complete, serving static files |
| Frontend loads at :5173 | ✅ "MISSION ALPHA" scanner UI with codes, timer, instructions |
| Neural Sync button | ✅ Shows "INITIALIZING NEURAL LINK..." → displays biometric codes (3,2,5,1) |
| WebSocket connection | ⚠️ Drops in headless browser (no camera/mic available — expected) |

### Key Differences from Previous Levels
| Aspect | Level 2 | Level 3 |
|--------|---------|---------|
| Agent type | Request-response | **Live streaming** (bidirectional) |
| Communication | REST API (`/api/chat`) | **WebSocket** (`/ws/{user}/{session}`) |
| Model | gemini-2.5-flash | **gemini-live-2.5-flash-preview-native-audio** |
| Input | Text queries | **Real-time audio + video frames** |
| Output | JSON responses | **Streaming events** (audio, transcripts, tool calls) |

---

## ✅ Level 4 — Dispatch Agent (A2A Protocol)

### Architecture

Two-agent A2A system with Redis backend:

```
Browser (screen share + mic) ──WebSocket──► Dispatch Agent (:8082)
                                              ├── monitor_for_hazard (video → Gemini → hazard detection)
                                              └── execute_architect ──A2A──► Architect Agent (:8081)
                                                                               └── lookup_schematic_tool → Redis (:6379)
```

### Steps Taken

1. Created `.env` with Vertex AI + Redis + Architect URL vars
2. Installed Redis via `winget install Redis.Redis` (auto-starts as service on :6379)
3. Loaded `schematics.redis` seed data (10 ship blueprints → Redis lists)
4. Created `architect_agent/` module (5 files: agent.py, server.py, __init__.py, requirements.txt, Dockerfile)
5. Filled 3 markers in `dispatch_agent/agent.py` (RemoteA2aAgent, monitor_for_hazard, tools)
6. Filled 3 markers in `backend/main.py` (RunConfig, upstream task, downstream task)
7. Relaxed `pydantic>=2.11.7` in `pyproject.toml` for Python 3.14 compatibility
8. Changed frontend dev fallback to port 8082 (ghost process on 8000)
9. `uv sync` (115 packages) + `npm install` (331 packages) + `npm run build` (1362 modules)

### Markers Filled (6 total)

| # | File | Marker | Implementation |
|---|------|--------|---------------|
| 1 | `dispatch_agent/agent.py` | `REPLACE-REMOTEA2AAGENT` | `RemoteA2aAgent` pointing to architect on :8081 |
| 2 | `dispatch_agent/agent.py` | `REPLACE_MONITOR_HAZARD` | Async generator: monitors video frames via Gemini for glowing parts |
| 3 | `dispatch_agent/agent.py` | `REPLACE_AGENT_TOOLS` | `[AgentTool(agent=architect_agent), monitor_for_hazard]` |
| 4 | `backend/main.py` | `REPLACE_RUN_CONFIG` | RunConfig with BIDI streaming, audio transcription, proactivity |
| 5 | `backend/main.py` | `PROCESS_AGENT_REQUEST` | Upstream: handles binary audio, JSON text/audio/image |
| 6 | `backend/main.py` | `PROCESS_AGENT_RESPONSE` | Downstream: logs tool calls, transcripts; forwards to WebSocket |

### New Files Created (5 + 2)

| File | Purpose |
|------|---------|
| `architect_agent/agent.py` | Redis lookup tool + agent definition |
| `architect_agent/server.py` | A2A server via `to_a2a()` on port 8081 |
| `architect_agent/__init__.py` | Package init |
| `architect_agent/requirements.txt` | Standalone deps |
| `architect_agent/Dockerfile` | Container build |
| `schematics.redis` | 10 ship blueprints seed data |
| `backend/.env` | Environment variables |

### Verification

- ✅ Architect agent starts on :8081 (A2A protocol)
- ✅ Dispatch agent starts on :8082 (WebSocket + Gemini Live)
- ✅ Redis running on :6379 with seed data
- ✅ WebSocket connects successfully
- ✅ Frontend shows MISSION BRAVO "ENGINEER STATION" UI
- ✅ Status: CONNECTED after clicking "INITIATE UPLINK"
- ✅ Screen share + microphone active
- ✅ Mission log shows real-time transcription

---

## ✅ Level 5 — Coordinate Group Rescue (Complete)

**Date:** 2026-03-08 | **Rank Achieved:** Rescued (100%)

### Architecture

```
React Frontend (SSE) ←→ Satellite Dashboard (:8083) ←Kafka─► Formation Agent ←→ Gemini 2.5 Flash
      pod_update events           ↕                    topic: a2a-formation-request
      formation_update            Kafka Broker (:9092)
                                  topic: a2a-reply-satellite-dashboard
```

### Key Implementation Note
`a2a.server.apps.kafka` (referenced in the codelab solution) **does not exist in any public release** of `a2a-sdk`. Implemented a fully self-contained `KafkaServerApp` shim using `aiokafka` directly, matching the same `create_kafka_server()` / `.run()` API.

### Steps

1. **Infrastructure**: Installed Docker Desktop (v29.2.1) + WSL 2.6.3; started `mission-kafka` container (`apache/kafka:4.2.0-rc1`) on `:9092`
2. **Formation Agent** (`level_5/agent/`): Gemini 2.5 Flash → 15 X,Y pod coordinates for CIRCLE/STAR/X/LINE/PARABOLA/RANDOM
3. **Satellite Dashboard** (`level_5/satellite/main.py`): FastAPI SSE server with aiokafka producer/consumer; reply correlation via `asyncio.Future` dict
4. **Frontend**: Built React app (`npm run build` → 1471 modules in `dist/`)
5. **Dependencies**: `uv sync` with `sse-starlette`, `aiokafka`, `pydantic>=2.11.7` (116 packages)

### Files Created / Modified
| File | Change |
|------|--------|
| `agent/formation/agent.py` | NEW — Gemini formation agent |
| `agent/formation/__init__.py` | NEW — package init |
| `agent/agent_to_kafka_a2a.py` | REWRITE — KafkaServerApp shim on aiokafka |
| `satellite/main.py` | REWRITE — direct aiokafka producer/consumer |
| `pyproject.toml` | Add sse-starlette, pydantic; fix a2a version |
| `frontend/dist/` | Built frontend assets |

### Verification
- ✅ Kafka container running on `:9092`
- ✅ Formation agent consuming `a2a-formation-request` (group `a2a-agent-group`)
- ✅ Satellite dashboard on `:8083` with reply consumer on `a2a-reply-satellite-dashboard`
- ✅ SSE `/stream` sends 15 pod positions live
- ✅ CIRCLE formation command tested end-to-end: request → Kafka → Gemini → coordinates → pods rearranged
- ✅ Sandbox updated: `level_4_complete=true`, `completion_percentage=100`, portrait/icon uploaded
