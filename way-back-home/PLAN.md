# 🚀 Way Back Home — Project Plan

**Explorer:** ExplorerMz | **Participant ID:** ee34c542 | **Event:** sandbox
**Crash Site Coordinates:** (56, 66) | **Biome:** VOLCANIC (NE quadrant)
**Live Map:** https://waybackhome.dev/e/sandbox

---

## Progress Overview

| Level | Mission | Status | Key Tech |
|-------|---------|--------|----------|
| **L0** | Generate explorer identity | ✅ Complete | Gemini image generation, multi-turn chat |
| **L1** | Pinpoint crash location | ✅ Complete | ADK, MCP servers, ParallelAgent, BigQuery |
| **L2** | Survivor Network | ✅ Complete | Cloud Spanner, Property Graph, RAG, Vertex AI |
| **L3** | Process SOS signals | ✅ Complete | FastAPI, Gemini Live API, WebSocket, native audio |
| **L4** | Dispatch Agent | ✅ Complete | A2A SDK, RemoteA2aAgent, Redis, hazard monitoring, Gemini Live |
| **L5** | Coordinate Group Rescue | ✅ Complete | aiokafka, KafkaServerApp shim, Gemini 2.5 Flash, SSE, React |

### Rank Progression

| Level Completed | Rank | Meaning |
|-----------------|------|---------|
| — | **Stranded** | Just crashed on the alien planet |
| L0 | **Survivor** | Generated identity, registered on the map |
| L1 | **Explorer** | Pinpointed crash location, activated beacon |
| L2 | **Navigator** | Built survivor network, can search + navigate connections |
| L3 | **Pathfinder** | Processing SOS signals, responding to emergencies |
| L4 | **Homebound** | Dispatching rescue agents, coordinating routes home |
| L5 | **Rescued** | Full group rescue complete — you made it home |

---

## ✅ Level 0 — Identify Yourself (Complete)

**Goal:** Generate a unique explorer avatar and register on the world map.

**What was built:**
- Multi-turn Gemini image generation chat session
- Portrait + icon generated in one consistent session (same art style)
- **Bonus:** Photo-based avatar — real likeness preserved with space explorer style
- Avatar registered via `create_identity.py` → ExplorerMz visible on live map

**Files:** `level_0/generator.py`, `level_0/create_identity.py`

---

## ✅ Level 1 — Pinpoint Location (Complete)

**Goal:** Build a multi-agent system to analyze crash site evidence and activate the rescue beacon.

**Architecture:**
```
MissionAnalysisAI (Root Agent)
├── before_agent_callback → fetches participant data, sets state
├── EvidenceAnalysisCrew (ParallelAgent) ← runs 3 analysts concurrently
│   ├── GeologicalAnalyst  → analyze_geological (custom MCP → Cloud Run)
│   ├── BotanicalAnalyst   → analyze_botanical  (custom MCP → Cloud Run)
│   └── AstronomicalAnalyst → extract_star_features (local) + execute_query (BigQuery MCP)
└── confirm_location tool  → PATCH /participants/{id}/location → beacon activated
```

**Results:**
- 🔬 Geological: **VOLCANIC 95%** (dark volcanic rock, sulfur, active lava crack)
- 🌿 Botanical: **VOLCANIC 100%** (fire blooms, obsidian sprouts, crackling/rumbling audio)
- ✅ 2-of-3 consensus → beacon activated at **(56, 66) · NE quadrant**

**Key ADK Patterns learned:**
- `before_agent_callback` for state setup without config file imports
- `{key}` state templating in agent instructions
- `ParallelAgent` for concurrent independent analyses
- `MCPToolset` with `StreamableHTTPConnectionParams` (custom + Google Cloud MCP)
- `ToolContext` for tools to read shared state
- Mixing local `FunctionTool` with remote `MCPToolset` in one agent

**Files:** `level_1/agent/`, `level_1/mcp-server/main.py`

---

## ✅ Level 2 — Survivor Network (Complete)

**Goal:** Build a graph-based survivor social network with AI-powered natural language querying.

**What was built:**
- **Cloud Spanner** Property Graph (`SurvivorGraph`) — Survivors, Skills, Needs, Resources, Biomes
- **FastAPI backend** with ADK agent — hybrid search (keyword + RAG/embeddings + combined)
- **React frontend** — 3D space-themed graph visualization + Mission Control AI chat
- **Multimedia pipeline** — SequentialAgent for upload → extract → save → summarize
- **Optional Memory Bank** — session persistence via Vertex AI Agent Engine

**Architecture:**
```
FastAPI Backend (port 8000)
├── /health, /api/chat, /api/graph, /api/upload
├── survivor_network_agent (ADK Agent)
│   ├── hybrid_search, semantic_search, keyword_search, find_similar_skills
│   ├── get_survivors_with_skill, get_all_survivors, get_urgent_needs
│   └── MultimediaExtractionPipeline (SequentialAgent)
│       └── upload → extraction → spanner_save → summary
├── HybridSearchService → Cloud Spanner (keyword + RAG via ML.PREDICT)
├── GraphService → Cloud Spanner Property Graph (GQL queries)
└── GCSService → Cloud Storage (media uploads)

React Frontend (port 5173)
├── 3D graph visualization (Three.js)
├── Mission Control AI chat panel
└── Hand tracking camera control
```

**13 TODOs filled across 7 files**, verified with 3-pass review protocol.

**Files:** `level_2/backend/`, `level_2/frontend/`

---

## ✅ Level 3 — Process SOS Signals (Complete)

**Goal:** Build a real-time biometric scanner using Gemini Live API and bidirectional WebSocket streaming.

**What was built:**
- **Biometric Agent** — ADK agent with `report_digit` tool, native audio model
- **WebSocket server** — bidirectional streaming (upstream: browser→queue, downstream: Gemini→browser)
- **React frontend** — "MISSION ALPHA" scanner UI with countdown timer, biometric codes, hand gesture detection
- **Native audio** — supports proactive audio, affective dialog, input/output transcription

**Architecture:**
```
Browser (camera + mic) ──WebSocket──► FastAPI (port 8080)
                                         ├── upstream_task: WS → LiveRequestQueue
                                         ├── downstream_task: runner.run_live() → WS
                                         └── biometric_agent (ADK Agent)
                                              ├── model: gemini-live-2.5-flash-preview-native-audio
                                              ├── tool: report_digit(count)
                                              └── detects fingers, calls tool, confirms verbally
```

**8 markers filled across 2 files** (`agent.py` — 4, `main.py` — 4).

**Files:** `level_3/backend/app/`, `level_3/frontend/`

---

## ✅ Level 4 — Dispatch Agent (Complete)

**Goal:** Build an intelligent rescue dispatch agent that routes teams around hazard zones.

**Architecture:**
```
Browser (cam + mic) ──WebSocket──► Dispatch Agent (port 8082)
                                       ├── monitor_for_hazard (video analysis)
                                       ├── lookup_schematic_tool → Redis
                                       └── RemoteA2aAgent → Architect Agent (port 8081)
                                            └── lookup_schematic_tool → Redis (blueprints)
```

**Files:** `level_4/backend/dispatch_agent/`, `level_4/backend/architect_agent/`

---

## ✅ Level 5 — Coordinate Group Rescue (Complete)

**Goal:** Full multi-agent orchestration — formation agent coordinates 15 rescue pods via Kafka.

**Architecture:**
```
React Frontend (SSE) ←→ Satellite Dashboard (:8083) ←Kafka─► Formation Agent ←→ Gemini 2.5 Flash
                              ↕                                      ↕
                        Pod positions                         Coordinate math
                        (15 pods, SSE)                       (circle/star/X/line)
                              ↕
                     Kafka Broker (:9092)
               topics: a2a-formation-request
                        a2a-reply-satellite-dashboard
```

**Key implementation decision:** `a2a.server.apps.kafka` doesn't exist in any public PyPI release of `a2a-sdk`. Implemented a self-contained `KafkaServerApp` shim using `aiokafka` directly, matching the expected API.

**Files:** `level_5/agent/`, `level_5/satellite/`, `level_5/frontend/`

---

## GCP Resources Used

| Resource | Name / ID |
|---|---|
| Project | `ai-hack-489018` |
| Region | `us-central1` |
| Service Account | `way-back-home-sa@ai-hack-489018.iam.gserviceaccount.com` |
| Artifact Registry | `way-back-home` (Docker) |
| MCP Server (Cloud Run) | `https://location-analyzer-avamvnovja-uc.a.run.app` |
| BigQuery Dataset | `ai-hack-489018.way_back_home.star_catalog` |
| Spanner Instance | `survivor-network` (ENTERPRISE) |
| Spanner Database | `graph-db` / Graph: `SurvivorGraph` |
| GCS Bucket | `gs://survivor-network-media-ai-hack-489018` |
