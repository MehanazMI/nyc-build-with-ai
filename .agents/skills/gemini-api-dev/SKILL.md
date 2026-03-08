---
name: gemini-api-dev
description: Build with the Gemini API using the latest google-genai SDK and models. Covers text, multimodal, function calling, structured output, embeddings, and context caching.
---

# Gemini API Development Skill

## Overview
The Gemini API provides access to Google's most advanced AI models. Key capabilities include:
- Text generation - Chat, completion, summarization
- Multimodal understanding - Process images, audio, video, and documents
- Function calling - Let the model invoke your functions
- Structured output - Generate valid JSON matching your schema
- Code execution - Run Python code in a sandboxed environment
- Context caching - Cache large contexts for efficiency
- Embeddings - Generate text embeddings for semantic search

## Current Gemini Models

> [!IMPORTANT]
> Models like `gemini-2.5-*`, `gemini-2.0-*`, `gemini-1.5-*` are legacy and deprecated. Use the new models below.

- `gemini-3-pro-preview` — 1M tokens, complex reasoning, coding, research
- `gemini-3-flash-preview` — 1M tokens, fast, balanced performance, multimodal
- `gemini-3-pro-image-preview` — 65k / 32k tokens, image generation and editing

## SDKs

> [!WARNING]
> Legacy SDKs `google-generativeai` (Python) and `@google/generative-ai` (JS) are deprecated. Migrate to the new SDKs urgently using the [Migration Guide](https://ai.google.dev/gemini-api/docs/migrate.md.txt).

- **Python**: `pip install google-genai`
- **JavaScript/TypeScript**: `npm install @google/genai`
- **Go**: `go get google.golang.org/genai`

---

## Quick Start

### Python
```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain quantum computing"
)
print(response.text)
```

### JavaScript/TypeScript
```typescript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});
const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: "Explain quantum computing"
});
console.log(response.text);
```

---

## API Spec (Source of Truth)

Always use the latest REST API discovery spec as the source of truth:
- **v1beta (default)**: `https://generativelanguage.googleapis.com/$discovery/rest?version=v1beta`
- **v1**: `https://generativelanguage.googleapis.com/$discovery/rest?version=v1`

Use v1beta unless explicitly pinned to v1.

## How to Use the Gemini API

For all documentation, fetch from the official docs index:
- **llms.txt URL**: `https://ai.google.dev/gemini-api/docs/llms.txt`

### Key Documentation Pages
- [Models](https://ai.google.dev/gemini-api/docs/models.md.txt)
- [Function calling](https://ai.google.dev/gemini-api/docs/function-calling.md.txt)
- [Structured outputs](https://ai.google.dev/gemini-api/docs/structured-output.md.txt)
- [Text generation](https://ai.google.dev/gemini-api/docs/text-generation.md.txt)
- [Image understanding](https://ai.google.dev/gemini-api/docs/image-understanding.md.txt)
- [Embeddings](https://ai.google.dev/gemini-api/docs/embeddings.md.txt)
- [SDK migration guide](https://ai.google.dev/gemini-api/docs/migrate.md.txt)

> [!IMPORTANT]
> These are not all the documentation pages. Use the `llms.txt` index to discover all available docs.

## When to Use
Use this skill for any task involving the Gemini API, Google GenAI SDK, multimodal AI, or Gemini model configuration.
