# 🌙 Bedtime Story Generator

Transform any photo(s) into personalized bedtime stories with audio narration.

---

## 🚀 Quick Start

```powershell
# Run the bedtime story generator
cd milestone_moments
python bedtime_app.py
```

**Input options:**
- Single photo: `playground.jpg`
- Multiple photos: `morning.jpg, afternoon.jpg, evening.jpg`
- Optional context: "First time on swings!" or leave blank

**Output:**
- Soothing bedtime story (200-300 words)
- Audio narration (when GCP credits active)
- Butterfly metaphor weaving
- Saved to `demo_outputs/`

---

## 📁 Project Structure

```
milestone_moments/
├── bedtime_app.py              # Main application
├── bedtime_storyteller.py      # Story generation agent
├── vision_agent.py             # Photo analysis (single/multi)
├── demo_outputs/               # Generated stories
├── TECHNICAL-OVERVIEW.md       # Full technical documentation
├── DEMO-TECHNICAL-GUIDE.md     # Demo preparation
└── PROJECT-PIVOT.md            # Design decisions
```

---

## 🎯 Core Features

### ✅ Multi-Photo Support
- Single photo → Simple bedtime story (200-250 words)
- Multiple photos → Full day narrative (250-300 words)
- AI weaves moments: "First you..., then you..., finally..."

### ✅ Optional Context
- Parent can add voice/text details
- Or let AI work with vision alone
- Graceful handling either way

### ✅ Constrained Generation
- 10-15 word sentences (child-friendly)
- Simple, soothing language
- Butterfly metaphor (gentle journey)
- Peaceful sleep imagery at end

### ✅ Audio Narration
- Gentle TTS for bedtime listening
- Text preprocessing for optimal voice
- Code ready (awaits GCP credits March 7)

---

## 🧪 Test It

```powershell
# Test mode (no photo needed)
python bedtime_app.py
# Press Enter when prompted for photo path
```

---

## 🏗️ Technical Highlights

**Multi-Agent Architecture:**
- Vision Agent (single/multi-photo analysis)
- Bedtime Storyteller (constrained generation)
- Audio Engine (TTS narration)

**Advanced Prompt Engineering:**
- Word count constraints (200-300)
- Sentence length limits (10-15 words)
- Tone enforcement (soothing bedtime)
- Metaphor consistency (butterfly journey)

**Multimodal Synthesis:**
- Photo(s) → Vision understanding
- Optional context → Enhanced narrative
- Text + Audio output

See [TECHNICAL-OVERVIEW.md](TECHNICAL-OVERVIEW.md) for full architecture.

---

## 🎬 Demo Files

- **DEMO-TECHNICAL-GUIDE.md** - Technical pitch & code walkthrough
- **PROJECT-PIVOT.md** - Why bedtime stories (vs milestone achievements)
- **TECHNICAL-OVERVIEW.md** - Complete system architecture

---

## 📅 Development Timeline

- **March 4:** MVP built (<30 min actual development)
- **March 5:** Multi-photo support added, documentation updated
- **March 7:** GCP credits → Enable audio narration
- **March 7-8:** Hackathon demo

---

## 💡 Use Cases

**Primary (Bedtime Stories):**
- Daily ritual: Any photo → Tonight's story
- Multi-photo days: Morning park + afternoon baking
- Universal appeal: Every parent, every child

**Secondary (Special Moments):**
- Achievement celebrations (first bike ride, snowboarding)
- Milestone memories (birthday, first day school)
- Triumph stories (like my son's butterfly journey)

---

## 🦋 The Personal Story

This project started with my son's snowboard photo. He struggled his first year (his "cocoon"). His mom never gave up. Now at 2.5, he's flying down mountains - like a butterfly.

I built this to celebrate his transformation. Then realized: every photo deserves this magic. Daily moments or life-changing triumphs. Every bedtime. Every butterfly.

---

**Every photo tells a story. Every story becomes a magical bedtime memory.** 🌙🦋
