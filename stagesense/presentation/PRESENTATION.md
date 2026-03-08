# StageSense — 5-Minute Demo Script

> **The AI that sees what you can't.**

---

## 🎯 Opening Hook (30 sec)

> *"Every presenter has a blind spot. You can't hear your own pace. You can't see your audience losing interest. StageSense is the AI that fills that gap — in real time, with zero text boxes."*

---

## 📱 Architecture Slide (30 sec)

Show the two-device setup:

```
📱 Phone (Speaker)          💻 Laptop (Dashboard)
   Camera + Mic       →       Live Scorecard
   WebSocket          →       SSE Stream
        ↓                          ↑
   ┌──────────────────────────────────┐
   │  Gemini Live API (Native Audio)  │
   │  ADK Runner + LiveRequestQueue   │
   │  FastAPI Backend on Cloud Run    │
   └──────────────────────────────────┘
```

**Key phrase:** *"Phone captures. Gemini analyzes. Dashboard displays. All in real time."*

---

## 🎤 Live Demo — Coach Mode (2 min)

1. **Open dashboard** on laptop → projector: `http://localhost:8080/dashboard.html`
2. **Open mobile page** on phone: `http://localhost:8080/`
3. Tap **COACH** mode → Tap **START SESSION**
4. **Start speaking** — narrate your demo naturally
5. **Point to dashboard** — scores updating live:
   - *"Watch my pace score... now I'll slow down... see it adjust"*
   - *"Notice the filler count — um, like — it catches those"*
   - *"The insight and action tips update every few seconds"*

**If scores aren't moving:** The simulation fallback keeps the demo alive with realistic scores.

---

## 👀 Live Demo — Room Read Mode (1 min)

1. Tap **ROOM READ** on phone
2. **Point camera at audience**
3. *"Now StageSense flips — it's reading YOU, the audience"*
4. Show engagement/confusion/excitement bars updating
5. *"If I see confusion spiking, I know to explain that concept again"*

---

## 🏗 Technical Deep Dive (30 sec)

> *"Under the hood:"*
> - **Gemini Live API** with native audio model — real-time bidirectional streaming
> - **Google ADK Runner** with LiveRequestQueue — same pattern as Way Back Home L3
> - **FastAPI** backend: WebSocket ingests audio/video, SSE pushes scores to dashboard
> - **No text box anywhere** — camera and microphone are the only input

---

## 💡 Closing (30 sec)

> *"StageSense coached me through THIS presentation. The very demo you just watched was being analyzed in real time. That's what breaking the text-box paradigm looks like."*

**Mic drop moment:** Point to dashboard showing the scores from your demo.

---

## 🛡 Backup Plans

| If this happens... | Do this |
|---------------------|---------|
| Gemini Live doesn't connect | Simulation fallback auto-activates — dashboard still updates |
| Phone mic doesn't work | Use laptop mic — open `http://localhost:8080/` on laptop too |
| Dashboard doesn't load | Refresh with Ctrl+Shift+R |
| Scores are all zeros | Speak louder / closer to mic — model needs speech audio |

---

## 📋 Pre-Demo Checklist

- [ ] Server running: `.venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8080`
- [ ] Dashboard open on laptop: `http://localhost:8080/dashboard.html`
- [ ] Mobile page open on phone: `http://localhost:8080/`
- [ ] Phone and laptop on same WiFi network
- [ ] Test START SESSION → speak → see scores move
- [ ] Browser mic permission granted
