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
4. The `solutions/` folder came from the upstream workshop repo (`google-americas/way-back-home`) and should never be committed to

---

## Project Overview

Way Back Home is a multi-level Google Cloud AI hackathon project. A space explorer (ExplorerMz) has crashed on an alien planet and must use AI agents to get rescued. Each level builds a different AI system.

```
level_0/   → Avatar generation (Gemini multi-turn image generation)
level_1/   → Crash site analysis (ADK multi-agent + MCP servers)
level_2/   → Survivor network (Cloud Spanner graph + Vertex AI)
level_3/   → SOS signal processing (event-driven agents, A2A)
level_4/   → Rescue dispatch agent (hazard-aware routing)
level_5/   → Group rescue coordination (Kafka + A2A)
solutions/ → Reference implementations for each level
PLAN.md    → High-level progress tracker
DEVLOG.md  → Step-by-step implementation notes
```

---

## Setup

### Prerequisites
- Python 3.11+ with `.venv` per level
- Google Cloud SDK (`gcloud`) authenticated
- GCP Project: `ai-hack-489018`, Region: `us-central1`
- Service Account: `way-back-home-sa@ai-hack-489018.iam.gserviceaccount.com`

### Level 1 Environment (primary working level)
```bash
cd way-back-home/level_1
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### Required Environment Variables
```bash
export GOOGLE_CLOUD_PROJECT="ai-hack-489018"
export GOOGLE_GENAI_USE_VERTEXAI="true"
export GOOGLE_CLOUD_LOCATION="us-central1"
export PARTICIPANT_ID="ee34c542"
export BACKEND_URL="https://api.waybackhome.dev"
export MCP_SERVER_URL="https://location-analyzer-avamvnovja-uc.a.run.app"
```

### Run the Agent Locally
```bash
# From way-back-home/level_1/
python -m google.adk.cli web --host 127.0.0.1 --port 8080
# Then open http://127.0.0.1:8080 → select "agent"
```

---

## Architecture (Level 1)

```
MissionAnalysisAI (Root Agent / ADK)
├── before_agent_callback → fetches participant data from backend API
├── EvidenceAnalysisCrew (ParallelAgent)
│   ├── GeologicalAnalyst  → MCPToolset → Cloud Run MCP → analyze_geological()
│   ├── BotanicalAnalyst   → MCPToolset → Cloud Run MCP → analyze_botanical()
│   └── AstronomicalAnalyst
│       ├── FunctionTool: extract_star_features() (local Gemini Vision)
│       └── MCPToolset → BigQuery MCP → execute_query()
└── FunctionTool: confirm_location() → PATCH /participants/{id}/location
```

**State flows** via `InvocationContext` — `before_agent_callback` sets `soil_url`, `flora_url`, `stars_url`, `x`, `y`, `project_id`, and sub-agents access them via `{key}` templating in their instructions.

---

## Key Files

| File | Purpose |
|------|---------|
| `level_1/agent/agent.py` | Root orchestrator — `before_agent_callback` + `ParallelAgent` + synthesis |
| `level_1/agent/agents/geological_analyst.py` | Soil sample specialist (custom MCP) |
| `level_1/agent/agents/botanical_analyst.py` | Flora video specialist (custom MCP) |
| `level_1/agent/agents/astronomical_analyst.py` | Star field specialist (local tool + BigQuery MCP) |
| `level_1/agent/tools/mcp_tools.py` | StreamableHTTP connection to Cloud Run MCP server |
| `level_1/agent/tools/star_tools.py` | Gemini Vision + Google Cloud BigQuery MCP |
| `level_1/agent/tools/confirm_tools.py` | Beacon activation via backend API |
| `level_1/mcp-server/main.py` | FastMCP server — `analyze_geological` + `analyze_botanical` |

---

## Code Style & Conventions

- **Python 3.11+** — type hints preferred
- **ADK agents**: Use `{key}` state templating in instructions (not f-strings)
- **Parallel agents**: Each agent gets its own `MCPToolset` instance — never share a singleton across parallel agents
- **MCP tools**: Custom tools use `StreamableHTTPConnectionParams`; Google-managed tools (BigQuery) use OAuth headers
- **ToolContext**: Tools read shared state via `tool_context.state.get("key")` — never import config directly
- **No secrets in code**: All sensitive values via environment variables only

---

## Test Commands

```bash
# Verify agent loads without errors
python -c "from agent.agent import root_agent; print(root_agent.name)"

# Run ADK web UI for interactive testing
python -m google.adk.cli web --host 127.0.0.1 --port 8080

# Test MCP server endpoint (should return tool list)
curl https://location-analyzer-avamvnovja-uc.a.run.app/mcp
```

---

## Deploy MCP Server (when changed)

```bash
cd way-back-home/level_1/mcp-server
$env:CLOUDSDK_PYTHON = "path/to/venv/python"   # Windows — avoids Python 3.14 gcloud bug
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions="_SERVICE_ACCOUNT=way-back-home-sa@ai-hack-489018.iam.gserviceaccount.com" \
  --project=ai-hack-489018
```

---

## GCP Resources

| Resource | Value |
|----------|-------|
| Project | `ai-hack-489018` |
| MCP Server (Cloud Run) | `https://location-analyzer-avamvnovja-uc.a.run.app` |
| BigQuery dataset | `ai-hack-489018.way_back_home.star_catalog` |
| Artifact Registry | `us-central1-docker.pkg.dev/ai-hack-489018/way-back-home` |
| Service Account | `way-back-home-sa@ai-hack-489018.iam.gserviceaccount.com` |

---

## ⚠️ Mandatory: Iterative Review Protocol

Before executing ANY level, perform **3 review passes**. Each pass catches what the previous one missed.

**Pass 1 — Scope Discovery** *(quick — will always miss things)*
- Read the level `README.md` and referenced docs
- List files that need changes, identify architecture and dependencies
- Draft initial plan with phases, files, and estimated effort

**Pass 2 — Deep Scan** *(thorough — catches most gaps)*
- `grep -rn "TODO\|REPLACE\|FIXME" level_X/ --include="*.py" --include="*.ts"`
- Read every TODO file line-by-line, map each to its `solutions/level_X/` counterpart
- Check for unlisted dependencies: env vars, GCP APIs, buckets, IAM roles
- Update plan with corrected counts; record what Pass 1 missed

**Pass 3 — Full Diff & Validation** *(comprehensive — catches everything)*
- Hash-compare ALL starter files vs solutions (not just TODO files)
- Classify diffs: `actionable` (logic) vs `cosmetic` (whitespace)
- Verify `.env` template covers every `os.getenv()` in the codebase
- Confirm infra commands are complete and correctly ordered
- Verify test plan has specific commands + expected outputs
- Record what Pass 2 missed

**Review Audit Table (required in every plan):**

| Pass | TODOs Found | Files Diffed | New Issues vs Previous |
|------|------------|-------------|----------------------|
| 1 — Scope | _count_ | — | _(baseline)_ |
| 2 — Deep Scan | _count_ | _count_ | _what was missed_ |
| 3 — Full Diff | _count_ | _all_ | _what was missed_ |

> **Rule: Do NOT execute until Pass 3 finds zero new actionable items.** If it does, run Pass 4.
> Save `implementation_plan.md` to `level_X/` after review is complete. Commit: `docs: level X implementation plan (reviewed)`.

### After Completing Each Level
- [ ] Update `PLAN.md` — mark level ✅, add architecture summary and GCP resources
- [ ] Update `DEVLOG.md` — add full step-by-step section with commands, TODOs table, and verification results
- [ ] `git add && git commit && git push` — all changes including docs

---

## Reference

- [PLAN.md](PLAN.md) — Level-by-level progress
- [DEVLOG.md](DEVLOG.md) — Step-by-step implementation notes with code
- [solutions/](solutions/) — Reference implementations for each level
- [ADK Docs](https://google.github.io/adk-docs/) — Agent Development Kit
- [FastMCP Docs](https://gofastmcp.com) — MCP server framework
