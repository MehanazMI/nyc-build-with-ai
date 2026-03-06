# Gemini API Quick Reference

## 🚀 Basic Setup

```python
import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
```

## 💬 Text Generation

```python
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='Tell me a story about AI'
)
print(response.text)
```

## 🎤 Voice/Audio Input

```python
# Upload audio file
audio_file = client.files.upload(path='audio.mp3')

response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents=[
        'What is being said in this audio?',
        audio_file
    ]
)
print(response.text)
```

## 👁️ Vision/Image Analysis

```python
# Upload image
image_file = client.files.upload(path='image.jpg')

response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents=[
        'Describe this image in detail',
        image_file
    ]
)
print(response.text)
```

## 🎨 Image Generation

```python
response = client.models.generate_images(
    model='imagen-3.0-generate-001',
    prompt='A futuristic AI robot helping people',
    number_of_images=1,
    aspect_ratio='1:1'
)

# Save generated image
response.generated_images[0].image.save('output.png')
```

## 🔄 Multi-turn Conversation

```python
chat = client.chats.create(
    model='gemini-2.0-flash-exp'
)

response1 = chat.send_message('Hello, I need help with AI')
print(response1.text)

response2 = chat.send_message('Can you explain more?')
print(response2.text)
```

## 🎭 System Instructions

```python
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='What should I do?',
    config={
        'system_instruction': 'You are a helpful AI assistant for a hackathon. Be encouraging and creative.'
    }
)
```

## 🔊 Text-to-Speech (via external library)

```python
# You might use Google Cloud Text-to-Speech
from google.cloud import texttospeech

tts_client = texttospeech.TextToSpeechClient()

synthesis_input = texttospeech.SynthesisInput(text="Hello from AI!")
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Neural2-J"
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

response = tts_client.synthesize_speech(
    input=synthesis_input,
    voice=voice,
    audio_config=audio_config
)

with open('output.mp3', 'wb') as out:
    out.write(response.audio_content)
```

## 🎬 Multimodal (Combined)

```python
# Analyze image AND audio together
image = client.files.upload(path='scene.jpg')
audio = client.files.upload(path='commentary.mp3')

response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents=[
        'Describe what you see and hear',
        image,
        audio
    ]
)
print(response.text)
```

## ⚙️ Configuration Options

```python
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='Write a creative story',
    config={
        'temperature': 0.9,           # Higher = more creative (0.0-2.0)
        'top_p': 0.95,                # Nucleus sampling
        'top_k': 40,                  # Top-k sampling
        'max_output_tokens': 2048,    # Max response length
        'stop_sequences': ['END']     # Stop generation at these
    }
)
```

## 🚦 Streaming Responses

```python
response = client.models.generate_content_stream(
    model='gemini-2.0-flash-exp',
    contents='Write a long story'
)

for chunk in response:
    print(chunk.text, end='', flush=True)
```

## 📝 Function Calling (Tools)

```python
def get_weather(location: str) -> str:
    return f"Weather in {location}: Sunny, 72°F"

tools = [{
    'function_declarations': [{
        'name': 'get_weather',
        'description': 'Get current weather for a location',
        'parameters': {
            'type': 'object',
            'properties': {
                'location': {
                    'type': 'string',
                    'description': 'City name'
                }
            }
        }
    }]
}]

response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='What is the weather in NYC?',
    config={'tools': tools}
)

# Handle function call
if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    if function_call.name == 'get_weather':
        result = get_weather(**dict(function_call.args))
        print(result)
```

## 🎯 Best Practices for Hackathon

### Model Selection
- **gemini-2.0-flash-exp**: Fastest, best for real-time
- **gemini-2.0-flash-thinking-exp**: For reasoning tasks
- **gemini-1.5-pro**: Most capable, slower
- **imagen-3.0-generate-001**: Image generation

### Prompt Engineering
```python
# ✅ Good prompt
prompt = """You are a real-time voice assistant for travelers.
The user will speak to you in their native language.
Translate to English and provide helpful travel tips.
Keep responses under 2 sentences."""

# ❌ Bad prompt  
prompt = "translate"
```

### Error Handling
```python
try:
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=user_input
    )
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
    # Fallback behavior
```

### Rate Limits
- Free tier: **15 requests/minute**
- With hackathon credits: **Higher limits**
- Use exponential backoff for retries

## 🔗 Quick Links

- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [API Reference](https://ai.google.dev/api)
- [Cookbook Examples](https://github.com/google-gemini/cookbook)
- [Model Cards](https://ai.google.dev/gemini-api/docs/models/gemini)

## 💡 Hackathon Tips

1. **Test API first** - Verify connectivity before building
2. **Cache responses** - Don't re-generate during demos
3. **Handle failures** - APIs can timeout
4. **Use streaming** - Better UX for long responses
5. **Combine modalities** - Voice + vision = impressive!

---

**Need help?** Check examples in the `examples/` folder!
