# NYC Build With AI Hackathon 2026
## Google Cloud Labs x Columbia Business School

🗓️ **Event Date:** March 7-8, 2026  
📍 **Location:** Columbia Business School, NYC

---

## 🎯 Project Overview

### 🌙 Current Project: Bedtime Story Generator
- ✅ **Track:** Creative Storyteller (rich, interleaved outputs)
- ✅ **Status:** MVP Complete - Multi-photo support enabled
- ✅ **Tech:** Gemini 2.5 Flash multimodal AI
- ⏳ **Audio:** Ready for GCP credits (March 7)

**What it does:** Transform any photo(s) into personalized bedtime stories optimized for listening.

See `milestone_moments/` folder for full implementation.

---

## 🛠️ Tech Stack

- **Google Gemini API** - Multimodal AI capabilities
- **Agent Development Kit (ADK)** - Agent orchestration
- **Google Cloud Platform** - Deployment & services
- **Python 3.13** - Primary language
- **Node.js 24** - Tooling & utilities

---

## 📚 Learning Path

### Day 1-2: Foundation
1. ✅ Environment Setup (COMPLETED)
2. ✅ [Level 0: Identity Generation](codelabs/level-0/) - Character generation with Gemini
3. ✅ [Level 1: Multi-Agent Systems](codelabs/level-1/) - Coordinated agent orchestration

### Day 3-4: Hackathon Track Preparation
- ✅ [Level 3: Live Multimodal Agent](codelabs/level-3/) - **Build experiences that see, hear, speak, and create**
  - 🎤 **Live Agent Track**: Real-time voice + vision interaction
  - ✨ **Creative Storyteller Track**: Rich narrative generation
- ✅ [Vision Agent Example](examples/vision-agent/) - Image & video processing  
- ⚠️ [Voice Agent Example](examples/voice-agent/) - Real-time audio (needs PyAudio)

### Day 5: Project Development
- Review [HACKATHON-TRACKS.md](codelabs/level-3/HACKATHON-TRACKS.md) - Choose your track!
- Pick from [HACKATHON-IDEAS.md](codelabs/level-3/HACKATHON-IDEAS.md) - 10 project ideas
- Use [hackathon-project/](hackathon-project/) template as starting point
- Build MVP prototype

### Day 6-7: Hackathon!
- Team formation (March 7)
- Hack day (March 8)
- Presentation & judging

---

## 🚀 Quick Start

### 1. Install Python Dependencies
```bash
pip install google-genai google-cloud-aiplatform
```

### 2. Authenticate with Google Cloud
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Get API Keys
- Get Gemini API key from [Google AI Studio](https://aistudio.google.com/)
- Save it to `.env` file (see `.env.example`)

### 4. Run Your First Agent
```powershell
# PowerShell (Windows)
cd examples\hello-gemini
python agent.py

# Or using semicolon for one-liners:
cd examples\hello-gemini; python agent.py
```

**Note:** If using Windows PowerShell 5.1, use `;` instead of `&&` to chain commands. See [POWERSHELL-GUIDE.md](POWERSHELL-GUIDE.md) for details.

---

## 📁 Project Structure

```
nyc-ai-hackathon-2026/
├── README.md                 # This file
├── QUICK-START.md           # Quick start guide
├── SETUP-GUIDE.md           # Setup instructions
├── GEMINI-CHEATSHEET.md     # API reference
├── .env                     # Your API keys (DO NOT COMMIT)
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
├── check-setup.py          # Environment verification
│
├── codelabs/               # Tutorial implementations
│   ├── level-0/           # ✅ Identity generation
│   │   ├── README.md
│   │   └── identity_generator.py
│   └── level-1/           # ✅ Multi-agent system
│       ├── README.md
│       └── multi_agent.py
│
├── examples/              # Sample agents
│   ├── hello-gemini/     # ✅ Basic Gemini integration
│   │   ├── README.md
│   │   └── agent.py
│   ├── voice-agent/      # ✅ Voice-enabled agent
│   │   ├── README.md
│   │   └── voice_agent.py
│   └── vision-agent/     # ✅ Vision capabilities
│       ├── README.md
│       └── vision_agent.py
│
└── hackathon-project/    # ✅ Your final project
    ├── README.md         # Project overview
    ├── PROJECT-PLAN.md   # Your project details
    ├── setup_project.py  # Project initialization
    ├── src/              # Source code
    ├── tests/            # Test files
    ├── docs/             # Documentation
    └── assets/           # Images, audio, etc.
```

---

## 🎁 Prizes

- 💰 $30,000 in Google Cloud Credits
- 🎫 4 tickets to Google I/O 2026
- 🛍️ $500 Google Store experience

---

## 🔗 Important Links

- [Event Page](https://gdg.community.dev/events/details/google-gdg-nyc-presents-nyc-build-with-ai-hackathon-google-cloud-labs-x-columbia-business-school-i-1/)
- [GDG NYC Slack](https://join.slack.com/t/gdg-nyc/shared_invite/zt-3quzwji4i-_3Qus3gr3FWa_xfiV8zaxQ)
- [Gemini API Docs](https://ai.google.dev/docs)
- [ADK Documentation](https://cloud.google.com/agent-development-kit/docs)

---

## 💡 Project Ideas

### Live Agent Category:
1. **Real-time Interpreter** - Translates speech + cultural gestures
2. **Vision Code Reviewer** - Screen share + voice code discussion
3. **Smart Shopping Assistant** - Camera-based product recommendations

### Creative Storyteller Category:
1. **Interactive Audio Drama** - Generated story + voice + sound effects
2. **Visual Novel Creator** - Dynamic story + images + character voices
3. **AI Bedtime Stories** - Adaptive storytelling based on child reactions

---

## 📝 Notes

- ❌ Don't build: Basic RAG, Medical/Mental health bots
- ✅ Do build: Immersive multimodal experiences
- Teams: 3-5 people recommended

---

**Good luck! Build something amazing! 🚀**
