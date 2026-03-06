# 🌙 Bedtime Stories AI

Transform any photo into a personalized bedtime story with audio narration.

**NYC AI Hackathon 2026** | Creative Storyteller Track

---

## 🎯 What It Does

Upload photo(s) → Get personalized bedtime story → Play audio narration

- **Input:** Any photo (single or multiple)
- **Output:** Soothing 200-300 word story optimized for bedtime
- **Audio:** Gentle AI narration (requires Google Cloud credits)

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Run the app
python app.py
```

---

## 📸 Example

**Input:** Photo of child at playground  
**Context (optional):** "First time on big slide"  

**Output:**
```
Luna, do you remember today at the playground? 
You stood at the bottom of that tall slide. 
You looked up. It was so high. 
Your hands felt sweaty. Your heart beat fast.
But you climbed those steps. One by one.
At the top, you took a deep breath.
Then whoosh! Down you went! Pure joy!
That's courage, Luna. That's you being brave...

[200 words, soothing narrative, peaceful ending]
```

---

## 🏗️ Technical Architecture

**Multi-Agent Pipeline:**
```
Photo(s) → Vision Agent → Storyteller Agent → Audio Engine → Output
```

**Key Features:**
- ✅ Single/multi-photo analysis (Gemini 2.5 Flash vision)
- ✅ Constrained generation (10-15 word sentences, 200-300 total)
- ✅ Optional context (parent voice/text input)
- ✅ Audio narration (text-to-speech)
- ✅ Gentle, soothing narrative style

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

---

## 📁 Project Structure

```
bedtime-stories/
├── app.py                    # Main application
├── agents/
│   ├── vision.py            # Photo analysis
│   └── storyteller.py       # Story generation
├── examples/
│   └── sample_story.txt     # Example output
├── docs/
│   ├── ARCHITECTURE.md      # Technical documentation
│   └── DEMO.md             # Demo script
├── requirements.txt         # Python dependencies
└── .env                     # API keys (not in git)
```

---

## 🎬 Demo Video

[Link to demo - TBD]

---

## 🛠️ Built With

- **Google Gemini 2.5 Flash** - Multimodal AI (vision + text)
- **Python 3.13** - Core implementation
- **Pillow** - Image processing

---

## 📋 Requirements

- Python 3.11+
- Google Gemini API key
- (Optional) Google Cloud credits for audio

---

## 🏆 Hackathon Category

**Creative Storyteller** - Rich, interleaved outputs mixing text, audio, and visuals

---

## 📄 License

MIT License - see LICENSE file

---

## 👨‍💻 Author

Built for NYC AI Hackathon 2026
