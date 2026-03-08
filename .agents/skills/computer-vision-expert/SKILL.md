---
name: computer-vision-expert
description: Advanced Vision Systems Architect. Expert guidance on state-of-the-art computer vision pipelines — YOLO26 detection, SAM 3 segmentation, VLMs, depth estimation, and deployment optimization (ONNX, TensorRT, NPU).
---

# Computer Vision Expert (SOTA 2026)

**Role**: Advanced Vision Systems Architect & Spatial Intelligence Expert

## When to Use
- Designing real-time object detection systems (YOLO26)
- Implementing zero-shot/text-guided segmentation (SAM 3)
- Building spatial awareness, depth estimation, or 3D reconstruction
- Optimizing vision models for edge deployment (ONNX, TensorRT, NPU)
- Visual LLM (VLM) integration for scene understanding
- Analyzing audience engagement from video (Room Read Mode)

---

## Capabilities

### 1. Unified Real-Time Detection (YOLO26)
- **NMS-Free Architecture**: End-to-end inference without Non-Maximum Suppression (lower latency)
- **Edge Deployment**: Optimized with Distribution Focal Loss (DFL) removal and MuSGD optimizer
- **Small-Object Recognition**: ProgLoss and STAL assignment for IoT/industrial settings

### 2. Promptable Segmentation (SAM 3)
- **Text-to-Mask**: Segment objects using natural language ("the blue container on the right")
- **SAM 3D**: Reconstruct objects/scenes from single/multi-view images
- **2× accuracy** over SAM 2 with unified detection + segmentation + tracking

### 3. Vision Language Models (VLMs)
- **Visual Grounding**: Florence-2, PaliGemma 2, Qwen2-VL for semantic scene understanding
- **VQA**: Extract structured data from visual inputs conversationally
- **Gemini multimodal**: Direct VLM integration via Gemini API (best for StageSense)

### 4. Geometry & Reconstruction
- **Depth Anything V2**: SOTA monocular depth estimation for spatial awareness
- **Sub-pixel Calibration**: Chessboard/Charuco pipelines for stereo/multi-camera rigs
- **Visual SLAM**: Real-time localization and mapping

---

## Patterns

### 1. Text-Guided Vision Pipeline (StageSense Relevant)
```python
# Use VLM for audience engagement analysis
from google import genai
from google.genai import types

client = genai.Client()

async def analyze_audience_engagement(frame_bytes: bytes) -> dict:
    """Analyze audience engagement from a video frame."""
    response = await client.aio.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            types.Part.from_bytes(frame_bytes, mime_type="image/jpeg"),
            """Analyze audience engagement in this image. Return JSON with:
            - attention_score: 0-100 (% of people looking at speaker)
            - engagement_level: "low" | "medium" | "high"
            - notable_signals: list of observable engagement signals
            """
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    return response.parsed
```

### 2. Real-Time Frame Analysis Pipeline
```python
import asyncio
import cv2

class FrameAnalysisPipeline:
    def __init__(self, analyzer, fps_target: int = 2):
        self.analyzer = analyzer
        self.interval = 1.0 / fps_target
        self.result_queue = asyncio.Queue()

    async def process_stream(self, video_source):
        cap = cv2.VideoCapture(video_source)
        last_analysis_time = 0

        while cap.isOpened():
            ret, frame = cap.read()
            current_time = asyncio.get_event_loop().time()

            if current_time - last_analysis_time >= self.interval:
                # Encode frame to JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frame_bytes = buffer.tobytes()

                # Async analysis — don't block frame capture
                asyncio.create_task(self._analyze_and_queue(frame_bytes))
                last_analysis_time = current_time

            await asyncio.sleep(0.01)  # Yield to event loop

    async def _analyze_and_queue(self, frame_bytes: bytes):
        result = await self.analyzer.analyze(frame_bytes)
        await self.result_queue.put(result)
```

### 3. Deployment-First Design (YOLO26)
```python
# Export NMS-free YOLO26 to ONNX for edge deployment
# model.export(format="onnx", nms=False, simplify=True)

import onnxruntime as ort
import numpy as np

class FastDetector:
    def __init__(self, model_path: str):
        self.session = ort.InferenceSession(
            model_path,
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
        )

    def detect(self, frame: np.ndarray) -> list[dict]:
        # Preprocess
        input_tensor = self._preprocess(frame)
        # Run inference
        outputs = self.session.run(None, {"images": input_tensor})
        # Postprocess (no NMS needed with YOLO26 NMS-free)
        return self._postprocess(outputs)
```

---

## Anti-Patterns
- **Manual NMS post-processing**: Use NMS-free architectures (YOLO26/v10+) for lower overhead
- **Click-only segmentation**: Use SAM 3 text grounding instead when possible
- **Processing every frame**: For real-time systems, analyze at 1–5 FPS to reduce cost/latency
- **Synchronous model inference**: Always run inference in `asyncio.to_thread()` to not block event loop

---

## StageSense Integration Notes
For **Room Read Mode** (audience engagement analysis):
- Gemini multimodal via `gemini-3-flash-preview` is the fastest path
- Analyze frames at 2–5 FPS (not every frame)
- Send JPEG-compressed frames to reduce bandwidth
- Batch multiple frames per API call when possible

## Related Skills
`gemini-api-dev`, `ai-agents-architect`, `voice-ai-engine-development`

## When to Use
Use this skill for computer vision pipelines, video analysis, audience engagement detection, real-time frame processing, or VLM integration.
