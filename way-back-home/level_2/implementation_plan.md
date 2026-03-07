# Level 2: Survivor Network — Implementation Plan (Final)

## What We're Building

Full-stack **Survivor Network**: Cloud Spanner property graph + FastAPI + ADK Agent + React frontend with hybrid search (keyword/semantic/combined), multimedia extraction pipeline, and optional Memory Bank.

## Review Summary

| Review Pass | What Changed |
|---|---|
| 1st | Found 6 TODOs in `agent.py` |
| 2nd | Found **13 TODOs across 7 files** (7 more missed) |
| 3rd | Found additional infra needs: `GCS_BUCKET_NAME`, `REGION` env vars, ENTERPRISE Spanner edition, `setup_data.py` handles everything |

---

## 13 TODOs Across 7 Files

| # | File | TODO | What to Add |
|---|------|------|-------------|
| 1 | `agent/agent.py:12` | `REPLACE_ADD_SESSION_MEMORY` | `add_session_to_memory()` callback |
| 2 | `agent/agent.py:39` | `REPLACE_SEARCH_LOGIC` | `semantic_search` description in instruction |
| 3 | `agent/agent.py:123` | `ADD_SEARCH_TOOL` | `semantic_search` in tools list |
| 4 | `agent/agent.py:130` | `REPLACE_ADD_MEMORY_BANK_TOOL` | `PreloadMemoryTool()` conditional |
| 5 | `agent/agent.py:139` | `REPLACE_ADD_SUBAGENT` | `sub_agents=[multimedia_agent]` |
| 6 | `agent/agent.py:141` | `REPLACE_ADD_CALLBACK` | `after_agent_callback` conditional |
| 7 | `api/routes/chat.py:31` | `REPLACE_VERTEXAI_SERVICES` | VertexAI session + memory services |
| 8 | `api/routes/chat.py:36` | `REPLACE_INMEMORY_SERVICES` | InMemory session + memory services |
| 9 | `api/routes/chat.py:41` | `REPLACE_RUNNER` | `Runner()` initialization |
| 10 | `tools/hybrid_search_tools.py:146` | `REPLACE_SEMANTIC_SEARCH_TOOL` | Full `semantic_search()` function |
| 11 | `agent/multimedia_agent.py:92` | `REPLACE_ORCHESTRATION` | `sub_agents=[upload, extract, save, summary]` |
| 12 | `services/hybrid_search_service.py:361` | `REPLACE_SQL` | RAG SQL with `COSINE_DISTANCE` |
| 13 | `deploy_agent.py:61` | `SET_UP_TOPIC` | Custom memory topics |

> [!NOTE]
> `graph_service.py:121` has a TODO but it's **non-blocking** — falls back to `get_full_graph()`.

---

## Phase 1 — GCP Infrastructure + Config

### 1a. Create `.env` file

Create `level_2/backend/.env`:
```
PROJECT_ID=ai-hack-489018
INSTANCE_ID=survivor-network
DATABASE_ID=graph-db
GRAPH_NAME=SurvivorGraph
REGION=us-central1
LOCATION=us-central1
USE_MEMORY_BANK=false
GCS_BUCKET_NAME=survivor-network-media-ai-hack-489018
```

### 1b. Enable APIs + Create GCS Bucket

```bash
gcloud services enable spanner.googleapis.com storage.googleapis.com
gsutil mb -l us-central1 gs://survivor-network-media-ai-hack-489018
```

### 1c. Run setup_data.py (handles EVERYTHING)

```bash
cd way-back-home/level_2/backend
pip install uv   # if not installed
uv sync
uv run python setup_data.py --project=ai-hack-489018
```

> [!IMPORTANT]
> `setup_data.py` creates the Spanner instance (ENTERPRISE edition), database, all tables, sample data, AND both property graphs in one script. No manual gcloud spanner commands needed.

---

## Phase 2 — Fill All 13 TODOs

Each TODO's replacement code comes directly from `solutions/level_2/`.

> [!TIP]
> All TODOs are small — 1-15 lines each. The solutions are straightforward drop-ins.

---

## Phase 3 — Optional: Deploy Agent Engine (Memory Bank)

Only needed if `USE_MEMORY_BANK=true`:
```bash
uv run python deploy_agent.py
# → Copy AGENT_ENGINE_ID to .env
```

---

## Phase 4 — Run Locally

```bash
# Backend (terminal 1)
cd way-back-home/level_2/backend
uv run uvicorn main:app --reload --port 8000

# Frontend (terminal 2)
cd way-back-home/level_2/frontend
npm install
npm run dev   # → http://localhost:5173
```

---

## Verification Plan

1. `curl http://localhost:8000/health` → `{"status": "ok"}`
2. Frontend graph visualization at `http://localhost:5173`
3. Chat test queries:
   - `"Find someone with healing skills in the mountains"` → hybrid
   - `"Who is good at fixing injuries?"` → semantic
   - `"List all medical skills"` → keyword
4. Spanner console: verify 4 survivors, 10 skills, 7 needs, property graph
