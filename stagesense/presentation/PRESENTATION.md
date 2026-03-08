# StageSense — Demo Script

> **Team: The Sixth Sense** | **Project: StageSense**
> *The AI that sees what you can't.*

---

## 🎯 Opening (30 sec)

> *"Every presenter has a blind spot. You can't hear your own filler words. You can't see your audience losing interest. StageSense is the AI that fills that gap — live, with no text boxes."*

---

## 📐 How It Works (30 sec)

> *"Two phones. Two angles. One AI."*

```
📱 Phone → WebSocket → Gemini Live API → ADK Agent → SSE → 💻 Dashboard
```

- **Coach Mode**: face camera at speaker → live pace / clarity / energy / filler scores
- **Room Read Mode**: face camera at audience → live engagement / confusion / excitement

---

## 🎤 Live Demo — Coach Mode (2 min)

1. Open **dashboard** on laptop: `http://localhost:8080/dashboard.html`
2. Open **mobile page** on phone: `http://localhost:8080/`
3. Select **COACH** → tap **START SESSION** → **speak**
4. Narrate the demo — *"Watch pace score... I'll speed up... now slow... see it react"*
5. *"Filler count — um, like — it catches every one"*
6. *"Insight and action tips update every few seconds"*

---

## 👀 Live Demo — Room Read Mode (1 min)

1. Tap **ROOM READ** on phone → point camera at audience
2. *"Now the AI flips — it reads YOU"*
3. Show engagement / confusion / excitement bars updating live
4. *"Confusion spiking? I know to re-explain. Excitement dropping? Time to land the point."*

---

## ⚙️ Tech (30 sec)

> - **Gemini Live API** — native audio model, real-time bidi streaming
> - **Google ADK Runner + LiveRequestQueue** — same stack as Way Back Home
> - **FastAPI** — WebSocket ingests A/V, SSE pushes scores to dashboard
> - **Zero text boxes** — mic and camera are the only inputs

---

## 💡 Close (30 sec)

> *"StageSense coached me through THIS presentation. The scores on that dashboard? They were real. That's what breaking the text-box paradigm actually looks like."*

**👉 Point to dashboard.** Mic drop.

---

## 🛡 If Things Go Wrong

| Issue | Fix |
|-------|-----|
| Scores stuck at zero | Speak louder — model responds to speech, not silence |
| Session won't start | Refresh `http://localhost:8080/` |
| Dashboard blank | Ctrl+Shift+R to hard refresh |
| Gemini times out | Simulation fallback auto-activates — keep talking |

---

## ✅ Pre-Demo Checklist

- [ ] Server running (from `stagesense/backend/`):
  ```powershell
  $env:GOOGLE_GENAI_USE_VERTEXAI="true"; $env:GOOGLE_CLOUD_PROJECT="ai-hack-489018"; $env:GOOGLE_CLOUD_LOCATION="us-central1"
  .venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8080
  ```
- [ ] Dashboard open on laptop: `http://localhost:8080/dashboard.html`
- [ ] Mobile page open on phone (same WiFi): `http://localhost:8080/`
- [ ] Mic permission granted on both
- [ ] Test: START SESSION → speak → confirm scores move on dashboard
- [ ] Voiceover ready: `presentation/i_studio.mp3` (play while showing architecture.png)
