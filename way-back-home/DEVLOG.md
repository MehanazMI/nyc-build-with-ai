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

## 🔴 Level 2 — Survivor Network (Coming Next)

**What:** Graph-based survivor network with Cloud Spanner, AI natural language querying, React frontend.

*This section will be filled in as we build Level 2.*

---

## 🔴 Level 3 — Process SOS Signals (Planned)

*This section will be filled in as we build Level 3.*

---

## 🔴 Level 4 — Dispatch Agent (Planned)

*This section will be filled in as we build Level 4.*

---

## 🔴 Level 5 — Coordinate Group Rescue (Planned)

*This section will be filled in as we build Level 5.*
