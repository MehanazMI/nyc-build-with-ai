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
| **L3** | Process SOS signals | 🔴 Not started | FastAPI, event-driven agents, A2A |
| **L4** | Dispatch Agent | 🔴 Not started | Dispatch agent, hazard DB, A2A protocol |
| **L5** | Coordinate Group Rescue | 🔴 Not started | Kafka, agent-to-agent comms, satellites |

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

## 🔴 Level 3 — Process SOS Signals

**Goal:** Build an event-driven agent that listens for and processes incoming SOS broadcasts from other survivors.

**Key Tech:** FastAPI, event-driven agents, A2A (Agent-to-Agent) protocol

**Files:** `level_3/backend/`, `level_3/frontend/`

---

## 🔴 Level 4 — Dispatch Agent

**Goal:** Build an intelligent rescue dispatch agent that routes teams around hazard zones.

**What to build:**
- Dispatch agent with access to hazard database
- Route planning that avoids dangerous areas
- A2A communication to coordinate with other agents

**Key Tech:** ADK dispatch agent, hazard DB (`hazard_db.py`), A2A protocol

**Files:** `level_4/backend/dispatch_agent/`

---

## 🔴 Level 5 — Coordinate Group Rescue

**Goal:** Full multi-agent orchestration — your agent communicates with a satellite agent via Kafka to coordinate the final group rescue.

**What to build:**
- Satellite agent (server) that manages rescue coordination
- Kafka messaging bridge for agent-to-agent communication (`agent_to_kafka_a2a.py`)
- Frontend dashboard showing rescue progress

**Key Tech:** Apache Kafka, A2A over Kafka, satellite agents, event streaming

**Files:** `level_5/agent/`, `level_5/satellite/`

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
