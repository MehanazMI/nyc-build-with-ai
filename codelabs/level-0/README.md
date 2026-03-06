# Level 0: Space Explorer Avatar Generator
## Multi-Turn Image Generation with Gemini (Nano Banana 🍌)

> **Official Workshop Pattern:** Create consistent character avatars using Gemini's native image generation

## 🎯 Learning Objectives
- Multi-turn image generation for character consistency
- Prompt engineering for images (style, constraints, variables)
- Gemini Image API (Nano Banana) usage
- Chat sessions for maintaining visual context

## 📖 Tutorial Reference
Based on: https://codelabs.developers.google.com/way-back-home-level-0/instructions

## 🔧 What You'll Build

### Two Implementations:

1. **Text-Based Identity** (`identity_generator.py`) - Original learning example
   - Generates character data as JSON
   - Text-only output
   
2. **Image-Based Avatar** (`image_generator.py`) ⭐ **Official Workshop Pattern**
   - Generates actual character images
   - Portrait + Icon with consistency
   - Multi-turn chat technique

## 🚀 Running the Code

### Text Version (Learning Example)
```bash
cd codelabs/level-0
python identity_generator.py
```

### Image Version (Official Workshop) ⭐
```bash
cd codelabs/level-0
python image_generator.py
```

**Note:** Image generation uses `gemini-2.0-flash-exp` model.

## 📝 Key Concepts

### 🔑 The Critical Pattern: Chat Sessions for Consistency

**❌ Wrong (Independent API Calls):**
```
Call 1 → Person A
Call 2 → Person B  (Different!)
```

**✅ Correct (Chat Session):**
```
Turn 1 → Person A
Turn 2 → Person A  (Same!)
```

### Code Pattern

```python
# 1. Create chat with image generation
chat = client.chats.create(
    model="gemini-2.0-flash-exp",
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"]
    )
)

# 2. First turn: Portrait
response1 = chat.send_message("Create portrait...")

# 3. Second turn: Icon (remembers first!)
response2 = chat.send_message("Create icon of SAME character...")
```

### Prompt Engineering for Images

1. **Subject** - "Create a space explorer portrait"
2. **Variables** - {username}, {appearance}, {suit_color}
3. **Style** - "Pixar style", "digital illustration"
4. **Constraints** - "white background", "1:1 ratio"
5. **Consistency** - "SAME person, SAME face"

## 🎨 Extensions
- Add image generation for character portraits
- Create multiple character profiles
- Store identities in a database
- Build a character relationship graph

## 📚 Next Steps
After completing this level, move to:
- [Level 1: Multi-Agent Systems](../level-1/README.md)
