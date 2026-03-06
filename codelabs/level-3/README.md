# Level 3: Live Multimodal Agent
## "Build an experience that sees, hears, speaks, and creates"

> **NYC AI Hackathon 2026 - Live Agent Track**
> 
> Step out of the traditional "text box" paradigm. Build AI that truly connects through real-time voice and vision.

---

## 🎯 What You'll Build

### Live Agent Track Foundation

A **multimodal agent using Gemini Live API** that demonstrates:

**✨ Core Capabilities:**
- **👁️ Sees**: Real-time image/video analysis
- **🎤 Hears**: Voice input processing (text-based demo mode included)
- **💬 Speaks**: Natural conversational responses
- **🔄 Interrupts**: Handles conversation flow naturally
- **🧠 Remembers**: Maintains context across turns

**🎯 Hackathon-Ready For:**
- **Real-time translators** (sees foreign text + speaks translation)
- **Vision-enabled tutors** (analyzes homework + explains steps)
- **Accessibility assistants** (describes surroundings + guides navigation)
- **Interactive guides** (museum, shopping, travel)

**🚀 Why This Works:**
- Uses Gemini 2.5 Flash (fast, multimodal)
- Foundation for voice + vision projects
- Extensible to full Gemini Live API
- Demo-ready in < 200 lines

---

## 🏗️ Live Agent Architecture

```
┌──────────────────────────────────────┐
│         INPUT MODALITIES             │
│  👁️ Vision    🎤 Voice (text demo)  │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│      GEMINI LIVE API ENGINE          │
│   • Real-time processing             │
│   • Context maintenance              │
│   • Interruption handling            │
│   • Multimodal understanding         │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│         OUTPUT MODALITIES            │
│  💬 Text      🔊 Voice (future)      │
└──────────────────────────────────────┘

  ┌─────────────────────────────────┐
  │  CONVERSATION STATE MANAGER     │
  │  • Multi-turn context           │
  │  • Image history                │
  │  • User preferences             │
  └─────────────────────────────────┘
```

**Live Agent Key Principles:**
1. **Speed**: Responses in < 2 seconds
2. **Natural**: Conversational, not robotic
3. **Contextual**: Remembers the conversation
4. **Adaptive**: Handles interruptions and pivots
5. **Multimodal**: Seamlessly blends vision + language

---

## 🚀 Quick Start

### Basic Demo (No Camera Required)
```powershell
cd codelabs\level-3
python live_multimodal_agent.py
```

### Interactive Mode (With Webcam)
```powershell
python live_multimodal_agent.py --camera
```

---

## 📚 Key Features

### 1. **Real-Time Scene Analysis**
```python
# Continuously analyze what the camera sees
scene = agent.analyze_scene(frame)
# "I see a workspace with a laptop, coffee mug, and notebook"
```

### 2. **Contextual Q&A**
```python
# Ask questions about what's visible
response = agent.ask("What color is the mug?")
# "The mug is blue with white text on it"
```

### 3. **Multi-Turn Dialogue**
```python
# Maintains conversation history
agent.ask("What do you see?")
agent.ask("What could I use it for?")  # "it" refers to previous context
```

### 4. **Object Detection & Counting**
```python
# Identify and count objects
objects = agent.detect_objects()
# {"laptop": 1, "mug": 1, "books": 3}
```

---

## 🎨 Hackathon Extension Ideas

### Live Agent Track
1. **Vision-Enabled Tutor**
   - Student shows homework problem
   - Agent explains step-by-step
   - Provides hints without full answers

2. **Accessibility Assistant**
   - Describes surroundings
   - Reads signs and text
   - Warns of obstacles

3. **Real-Time Translator**
   - Sees foreign text/signs
   - Translates instantly
   - Speaks translation

4. **Shopping Assistant**
   - Scans product labels
   - Compares nutrition info
   - Suggests alternatives

### Creative Storyteller Track
1. **Photo Story Generator**
   - Captures scene
   - Creates narrative
   - Adds audio narration

2. **Art Explainer**
   - Analyzes artwork
   - Tells its story
   - Creates poetic description

---

## 🔧 Technical Stack

- **Gemini 2.5 Flash**: Fast multimodal model
- **Python 3.13**: Core language
- **OpenCV**: Camera capture (optional)
- **PIL/Pillow**: Image processing
- **google-genai SDK**: Gemini integration

---

## 📖 Learning Objectives

| Concept | What You Learn |
|---------|----------------|
| **Multimodal Input** | Process images + text simultaneously |
| **Conversation State** | Maintain context across interactions |
| **Real-Time Processing** | Low-latency responses |
| **Vision Understanding** | Scene analysis, object detection |
| **Natural Dialogue** | Human-like conversation flow |

---

## 🎯 Success Metrics

- ✅ Responds to images in < 2 seconds
- ✅ Maintains context for 5+ turns
- ✅ Handles interruptions gracefully
- ✅ Natural, conversational responses
- ✅ Accurate scene understanding

---

## 💡 Tips for Your Hackathon Project

1. **Start Simple**: Get basic vision + text working first
2. **Add Personality**: Give your agent a unique voice/style
3. **Focus UX**: How users interact matters more than complexity
4. **Demo Ready**: Have backup images if camera fails
5. **Clear Value**: Show how it solves a real problem

---

## 🚧 Next Steps

1. Run the basic demo to understand the flow
2. Experiment with different prompts/images
3. Add webcam support (optional)
4. Customize for your use case
5. Add voice output (TTS)
6. Deploy to Cloud Run (advanced)

---

## 📝 Notes

- **No Cloud Run needed**: Runs locally for development
- **Simplified**: Focuses on core concepts, not production deployment
- **Extensible**: Easy to add features for your hackathon idea
- **Hackathon-Ready**: Complete working demo in ~200 lines

---

**Ready to build something amazing? Let's go! 🚀**
