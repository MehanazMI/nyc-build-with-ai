# Vision Agent - Multimodal Image & Video Processing

## 🎯 What This Is
An AI agent that understands and analyzes images and videos using Gemini's vision capabilities.

## 👁️ Capabilities
- Image analysis and description
- Object detection and counting
- Scene understanding
- OCR (text extraction from images)
- Video frame analysis
- Visual question answering

## 🚀 Running the Agent

```bash
cd examples/vision-agent
python vision_agent.py
```

## 📋 Requirements
- Python 3.9+
- Gemini API key with vision support
- PIL/Pillow for image handling

## 🔧 Installation

```bash
pip install google-genai pillow python-dotenv
```

## 💡 Use Cases for Hackathon

### Live Agent Track
- **Visual Assistant**: Help visually impaired navigate environments
- **AR Tour Guide**: Real-time scene description and information
- **Safety Monitor**: Detect hazards or safety violations in real-time

### Creative Storyteller Track
- **Photo Story Generator**: Turn photos into narratives
- **Comic Book Creator**: Generate stories from image sequences
- **Visual Poetry**: Create poems inspired by images

## 🎨 Vision Capabilities

### Image Understanding
```python
# Describe image
response = analyze_image(image_path, "Describe this image in detail")

# Count objects
response = analyze_image(image_path, "How many people are in this image?")

# Extract text
response = analyze_image(image_path, "What text is visible in this image?")
```

### Complex Analysis
```python
# Scene understanding
response = analyze_image(image_path, """
What's the mood of this scene? 
What time of day is it?
What activities are happening?
""")

# Comparison
response = analyze_images([img1, img2], 
    "What are the differences between these images?")
```

## 📸 Sample Images

The `samples/` directory contains test images:
- `sample-scene.jpg` - Urban scene
- `sample-text.jpg` - Document/sign with text
- `sample-objects.jpg` - Multiple objects

## 🔥 Advanced Features

### Video Processing
Process video frame-by-frame for:
- Activity recognition
- Object tracking
- Scene changes
- Summarization

### Multi-Image Analysis
Compare and analyze multiple images:
- Before/after comparisons
- Similarity detection
- Visual storytelling across images

## 📚 Resources
- [Gemini Vision Guide](https://ai.google.dev/gemini-api/docs/vision)
- [Multimodal Prompting Tips](https://ai.google.dev/gemini-api/docs/multimodal)
