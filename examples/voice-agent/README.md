# Voice Agent - Gemini Live API

## 🎯 What This Is
A voice-enabled AI agent using Gemini's Live API for real-time audio conversations.

## 🎤 Capabilities
- Real-time speech-to-speech interaction
- Natural conversation with interruptions
- Low latency responses
- Voice modulation and control

## 🚀 Running the Agent

```bash
cd examples/voice-agent
python voice_agent.py
```

## 📋 Requirements
- Python 3.9+
- Microphone access
- Gemini API key
- Audio libraries (PyAudio)

## 🔧 Installation

```bash
pip install pyaudio google-genai python-dotenv
```

### Windows Users
If PyAudio installation fails:
```powershell
pip install pipwin
pipwin install pyaudio
```

## 💡 Use Cases for Hackathon

### Live Agent Track
- **Real-time Translator**: Speak in one language, hear response in another
- **Voice Tutor**: Interactive learning with voice feedback
- **Audio Tour Guide**: Location-aware voice guidance
- **Accessibility Assistant**: Voice-controlled helper for visually impaired

### Tips for Building
1. Keep latency low (< 500ms for natural feel)
2. Handle interruptions gracefully
3. Provide audio/visual feedback
4. Test with different accents/environments

## 🎨 Customization

### Voice Configuration
```python
voice_config = {
    "voice_name": "Puck",  # Aoede, Charon, Fenrir, Kore, Puck
    "speech_rate": 1.0,
    "pitch": 0
}
```

### System Instructions
```python
system_instruction = """You are a helpful voice assistant.
- Speak naturally and conversationally
- Keep responses concise (2-3 sentences)
- Ask clarifying questions when needed
- Be engaging and friendly"""
```

## 📚 Resources
- [Gemini Live API Docs](https://ai.google.dev/gemini-api/docs/live-api)
- [Voice Configuration Guide](https://ai.google.dev/gemini-api/docs/audio)
