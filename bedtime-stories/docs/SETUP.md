# 🚀 Development Setup

## Quick Start

```bash
# Clone repository
git clone <repo-url>
cd bedtime-stories

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Test the app
python app.py
# Press Enter for demo mode
```

---

## Requirements

- **Python:** 3.11 or higher
- **API Key:** Google Gemini API key
- **Dependencies:** See `requirements.txt`

---

## Environment Setup

### 1. Get Gemini API Key

1. Visit https://aistudio.google.com/apikey
2. Create or select a project
3. Generate API key
4. Copy key to `.env` file

### 2. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env
GEMINI_API_KEY=your_api_key_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `google-genai>=0.8.0` - Official Gemini SDK
- `pillow>=10.0.0` - Image processing
- `python-dotenv>=1.0.0` - Environment management

---

## Running the App

### Interactive Mode

```bash
python app.py
```

Follow the prompts:
1. **Photo path(s):** Enter photo file path (or comma-separated for multiple)
2. **Child's name:** Enter child's name
3. **Context:** Optional context (press Enter to skip)

### Demo Mode

```bash
python app.py
# Press Enter when asked for photo path
```

Demo mode generates a sample story without requiring photos.

### Programmatic Use

```python
from app import BedtimeStoriesApp

app = BedtimeStoriesApp()

result = app.generate(
    photo_paths="path/to/photo.jpg",
    child_name="Luna",
    context="First time on the big slide",
    save_audio=True
)

print(result['story'])
print(f"Saved to: {result['saved_to']}")
```

---

## Project Structure

```
bedtime-stories/
├── app.py                      # Main application
├── requirements.txt            # Python dependencies
├── .env                        # API keys (not in git)
├── .env.example               # Template for .env
├── .gitignore                 # Git ignore rules
│
├── agents/
│   ├── __init__.py            # Package initialization
│   ├── vision.py              # Vision Agent
│   └── storyteller.py         # Storyteller Agent
│
├── outputs/                    # Generated stories
│   ├── <name>_story.txt       # Story text files
│   └── <name>_bedtime.mp3     # Audio files (optional)
│
├── docs/
│   ├── ARCHITECTURE.md        # Technical architecture
│   └── SETUP.md               # This file
│
└── README.md                   # Project overview
```

---

## Development Workflow

### 1. Make Changes

Edit code in `app.py` or `agents/` folder.

### 2. Test Changes

```bash
# Test with demo mode
python app.py
# Press Enter for demo

# Test with real photo
python app.py
# Enter photo path when prompted
```

### 3. Commit Changes

```bash
git add .
git commit -m "Description of changes"
git push
```

---

## Common Issues

### Issue: "GEMINI_API_KEY not found"

**Solution:** 
```bash
# Ensure .env file exists
ls .env

# Check .env has API key
cat .env

# Should see:
GEMINI_API_KEY=AIza...
```

### Issue: "Failed to analyze image"

**Possible causes:**
- Invalid photo path
- Unsupported image format
- API rate limit reached

**Solution:**
```bash
# Check file exists
ls path/to/photo.jpg

# Try with absolute path
python app.py
# Enter: C:\full\path\to\photo.jpg
```

### Issue: "Audio generation unavailable"

**Expected behavior:** Audio requires Google Cloud credits (distributed at hackathon)

**Current:** Text stories work fine, audio gracefully skipped

---

## Testing

### Test Demo Mode
```bash
python app.py
# Press Enter
# Verify demo story appears
# Check outputs/demo_story.txt exists
```

### Test Real Photo
```bash
python app.py
# Enter: path/to/photo.jpg
# Enter: TestChild
# Press Enter (skip context)
# Verify story generated
# Check outputs/testchild_story.txt
```

### Test Multi-Photo
```bash
python app.py
# Enter: photo1.jpg, photo2.jpg, photo3.jpg
# Enter: MultiTest
# Press Enter
# Verify longer story (250-300 words)
```

---

## Dependencies

### Core
- **google-genai (1.65.0)**: Gemini SDK for vision + text + audio
- **pillow (12.0.0)**: Image loading and processing
- **python-dotenv (1.1.1)**: Environment variable management

### Transitive
- anyio, httpx, pydantic, requests, etc. (installed automatically)

### Installing
```bash
pip install -r requirements.txt
```

---

## Environment Variables

Required in `.env`:

```bash
# Google Gemini API Key
GEMINI_API_KEY=your_api_key_here
```

Optional (for hackathon):
```bash
# Google Cloud Project (for audio features)
GOOGLE_CLOUD_PROJECT=your-project-id
```

---

## Git Workflow

### Initial Setup
```bash
git init
git add .
git commit -m "Initial commit: Bedtime Stories AI"
```

### Daily Workflow
```bash
# Pull latest
git pull

# Make changes
# ... edit files ...

# Stage changes
git add .

# Commit with message
git commit -m "Added multi-photo support"

# Push to remote
git push
```

---

## Troubleshooting

### Python Version
```bash
python --version
# Should be 3.11 or higher
```

### Check Dependencies
```bash
pip list | grep -E "google-genai|pillow|dotenv"
```

### Verify API Key
```python
from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv('GEMINI_API_KEY')[:10] + "...")
# Should print first 10 chars of key
```

---

## Support

**During Hackathon:**
- Ask at mentor desk
- Check Gemini API docs: https://ai.google.dev/

**General:**
- GitHub Issues
- API documentation
- Code comments

---

## Next Steps

1. ✅ Set up environment
2. ✅ Test demo mode
3. ✅ Test with real photo
4. 📝 Read [ARCHITECTURE.md](ARCHITECTURE.md)
5. 🎨 Customize story style
6. 🚀 Build your demo
