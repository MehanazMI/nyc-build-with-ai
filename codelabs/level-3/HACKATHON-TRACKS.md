# 🎯 NYC AI Hackathon 2026 - Track Guide
## "Build an experience that sees, hears, speaks, and creates"

---

## 🎪 The Two Tracks

### 🎤 Track 1: The Live Agent
**Mission:** Build real-time, voice-and-vision enabled agents that converse naturally and handle interruptions.

**Key Requirements:**
- ✅ **Real-time** interaction (low latency)
- ✅ **Voice** input/output (natural speech)
- ✅ **Vision** capabilities (see and understand)
- ✅ **Natural conversation** (not robotic)
- ✅ **Interruption handling** (adaptive dialogue)

**Examples from Prompt:**
- Real-time translators
- Vision-enabled tutors

**Your Code Foundation:**
- `live_multimodal_agent.py` - Vision + conversation agent
- Uses Gemini 2.5 Flash for speed
- Multi-turn context maintenance
- Ready for voice extension

---

### ✨ Track 2: The Creative Storyteller
**Mission:** Generate rich, interleaved outputs—seamlessly mixing text, audio, and visuals into cohesive narrative flow.

**Key Requirements:**
- ✅ **Rich content** generation (not simple text)
- ✅ **Multi-modal** outputs (text + audio + visuals)
- ✅ **Interleaved** seamlessly (not separate pieces)
- ✅ **Cohesive narrative** (tells a story)
- ✅ **Creative** and engaging (not factual chatbot)

**Examples You Can Build:**
- Photo story generators
- Art interpreters with narrative
- Travel memory creators
- Scene-to-screenplay converters

**Your Code Foundation:**
- `creative_storyteller.py` - Vision → rich narratives
- Multiple narrative styles
- Structured story generation
- Visual poetry creation

---

## 🎯 How to Choose Your Track

### Choose **Live Agent** if you want to build:
- 🗣️ Real-time conversation systems
- 👁️ Vision-based assistants
- ♿ Accessibility tools
- 🌍 Translation/interpretation
- 📚 Interactive tutoring
- 🏛️ Live guides (museum, shopping, etc.)

**Focus:** Speed, natural interaction, practical utility

---

### Choose **Creative Storyteller** if you want to build:
- 📖 Narrative generators
- 🎨 Artistic interpretations
- ✈️ Memory/experience creators
- 🎭 Poetic/dramatic content
- 🎬 Screenplay/script generation
- 👶 Children's content

**Focus:** Creativity, rich content, emotional engagement

---

## 🏗️ Technical Comparison

| Aspect | Live Agent | Creative Storyteller |
|--------|------------|---------------------|
| **Primary API** | Gemini Live API | Gemini Models API |
| **Speed Priority** | ⚡ Critical (< 2s) | 🎨 Quality over speed |
| **Temperature** | 0.7 (balanced) | 0.9-1.0 (creative) |
| **Output Type** | Conversational text | Rich structured content |
| **Context** | Multi-turn dialogue | Narrative cohesion |
| **User Interaction** | Continuous | Burst generation |
| **Voice** | Required | Optional (narration) |
| **Vision** | Real-time analysis | Deep interpretation |

---

## 💡 Hackathon Strategy

### For Live Agent Track:

**Phase 1: Core MVP (Hours 1-3)**
```python
✅ Image analysis working
✅ Text-based conversation
✅ Context maintenance
✅ Demo with 3 scenarios
```

**Phase 2: Voice Integration (Hours 3-5)**
```python
✅ Add speech-to-text input
✅ Add text-to-speech output
✅ Test interruption handling
✅ Improve response latency
```

**Phase 3: Polish & Demo (Hours 5-8)**
```python
✅ Add error handling
✅ Create demo script
✅ Practice 3-minute pitch
✅ Have backup plan
```

---

### For Creative Storyteller Track:

**Phase 1: Core MVP (Hours 1-3)**
```python
✅ Image → story generation
✅ 2-3 narrative styles
✅ Structured output (JSON)
✅ Basic formatting
```

**Phase 2: Rich Content (Hours 3-5)**
```python
✅ Add audio narration (TTS)
✅ Generate visual elements
✅ Create interleaved output
✅ Multiple story formats
```

**Phase 3: Experience Design (Hours 5-8)**
```python
✅ Build web interface
✅ Add sharing features
✅ Polish presentation
✅ Create demo content
```

---

## 🎨 Project Ideas by Track

### Live Agent Ideas

| Project | What It Does | Key Feature |
|---------|-------------|-------------|
| **Vision Tutor** | Analyzes homework, explains solutions | Step-by-step guidance |
| **Access Guide** | Describes surroundings for blind users | Real-time navigation |
| **Live Translator** | Sees + translates foreign text | Instant speech output |
| **Shop Assistant** | Scans products, compares options | Personalized advice |
| **Museum Guide** | Recognizes art, tells stories | Audio explanations |

### Creative Storyteller Ideas

| Project | What It Does | Key Feature |
|---------|-------------|-------------|
| **Photo Stories** | Captures scene → creative narrative | Multiple styles |
| **Art Poet** | Artwork → poetic interpretation | Audio narration |
| **Travel Diary** | Photos → memory book entries | Emotional resonance |
| **Kids Creator** | Drawing → bedtime story | Character voices |
| **Scene-to-Film** | Photo → movie screenplay | Dramatic dialogue |

---

## 🚀 Using Your Foundation Code

### For Live Agent Projects:
```bash
# Start with:
cd codelabs/level-3
python live_multimodal_agent.py --interactive

# Then customize:
# 1. Change system_instruction for your domain
# 2. Add voice I/O (speech recognition + TTS)
# 3. Optimize for real-time (reduce latency)
# 4. Add interruption handling
# 5. Create web/mobile interface
```

### For Creative Storyteller Projects:
```bash
# Start with:
cd codelabs/level-3
python creative_storyteller.py

# Then customize:
# 1. Add more narrative styles
# 2. Integrate text-to-speech (audio narration)
# 3. Generate accompanying visuals
# 4. Create multi-chapter stories
# 5. Build shareable output format
```

---

## ✅ Judging Criteria Alignment

### What Judges Look For:

1. **Innovation** 🌟
   - Live Agent: Novel interaction patterns
   - Creative Storyteller: Unique narrative approaches

2. **Technical Excellence** 💻
   - Live Agent: Low latency, smooth experience
   - Creative Storyteller: Rich, cohesive output

3. **User Experience** 🎨
   - Live Agent: Natural, intuitive conversation
   - Creative Storyteller: Engaging, emotional content

4. **Practical Value** 💡
   - Live Agent: Solves real problem
   - Creative Storyteller: Creates meaningful experiences

5. **Demo Quality** 🎬
   - Both: Clear 3-minute presentation
   - Both: Working prototype (no vaporware!)

---

## 🎯 Success Tips

### Do's ✅
- **Focus on ONE track** (don't mix both)
- **Start simple** then add complexity
- **Demo early** and often
- **Have backups** (sample content, cached responses)
- **Practice pitch** (3 minutes exactly)
- **Show, don't tell** (live demo > slides)

### Don'ts ❌
- **Don't overengineer** (working > perfect)
- **Don't ignore UX** (tech alone isn't enough)
- **Don't skip testing** (Murphy's law applies!)
- **Don't forget the "why"** (problem + solution)
- **Don't go overtime** (3 minutes is STRICT)

---

## 🏆 Final Checklist

### Live Agent Track:
- [ ] Responds in < 2 seconds
- [ ] Maintains conversation context (5+ turns)
- [ ] Handles vision input smoothly
- [ ] Natural conversational tone
- [ ] Graceful error handling
- [ ] Clear value proposition
- [ ] Working demo (with backup plan)

### Creative Storyteller Track:
- [ ] Generates rich, creative content
- [ ] Multiple output modalities
- [ ] Cohesive narrative flow
- [ ] Emotionally engaging
- [ ] Polished presentation
- [ ] Shareable/demonstrable output
- [ ] Working demo (with examples)

---

## 📚 Resources

**Official Documentation:**
- Gemini Live API: https://ai.google.dev/gemini-api/docs/live-api
- Agent Development Kit: https://cloud.google.com/vertex-ai/docs/agent-builder
- GenAI SDK: https://ai.google.dev/gemini-api/docs

**Your Local Resources:**
- `codelabs/level-3/live_multimodal_agent.py` - Live Agent foundation
- `codelabs/level-3/creative_storyteller.py` - Creative Storyteller foundation
- `codelabs/level-3/HACKATHON-IDEAS.md` - 10 project ideas

**Community:**
- Hackathon Slack: https://gdg-nyc.slack.com
- Event: March 7-8, 2026
- Venue: Columbia Business School

---

## 🎉 Remember

> **"Don't just build a chatbot. Build an experience that sees, hears, speaks, and creates."**

- **Live Agent:** It's about the CONVERSATION
- **Creative Storyteller:** It's about the EXPERIENCE

**You've got the foundation. Now make it YOURS! 🚀**

---

**Good luck! Build something amazing! 🏆**
