---
name: audio-transcriber
description: Automate audio-to-text transcription with professional Markdown output, meeting minutes, speaker diarization, and executive summaries. Uses Faster-Whisper or Whisper. Works universally across projects.
---

# Audio Transcriber

## Purpose
This skill automates audio-to-text transcription with professional Markdown output, extracting rich technical metadata (speakers, timestamps, language, file size, duration) and generating structured meeting minutes and executive summaries.

Uses **Faster-Whisper** or **Whisper** with zero configuration, working universally across projects without hardcoded paths or API keys.

---

## When to Use
Invoke this skill when:
- Transcribing audio/video files to text
- Generating meeting minutes automatically from recordings
- Needing speaker identification (diarization) in conversations
- Generating subtitles/captions (SRT, VTT formats)
- Creating executive summaries of long audio content
- User says: "transcribe this audio", "convert audio to text", "generate meeting notes from recording"

**Supported formats**: MP3, WAV, M4A, OGG, FLAC, WEBM

---

## Workflow

### Step 0: Discover Available Tools
```python
# Auto-detect: Faster-Whisper (preferred), Whisper, or Deepgram
try:
    from faster_whisper import WhisperModel
    TRANSCRIBER = "faster-whisper"
except ImportError:
    try:
        import whisper
        TRANSCRIBER = "whisper"
    except ImportError:
        TRANSCRIBER = "deepgram"  # Cloud fallback
```

### Step 1: Validate Audio File
```python
import os
from pathlib import Path

def validate_audio(file_path: str) -> dict:
    path = Path(file_path)
    supported = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    if path.suffix.lower() not in supported:
        raise ValueError(f"Unsupported format: {path.suffix}")

    size_mb = path.stat().st_size / (1024 * 1024)
    return {"path": str(path), "size_mb": round(size_mb, 2), "format": path.suffix}
```

### Step 2: Transcribe
```python
from faster_whisper import WhisperModel

def transcribe(audio_path: str, language: str = "auto") -> dict:
    model = WhisperModel("base", device="cpu", compute_type="int8")

    segments, info = model.transcribe(
        audio_path,
        language=None if language == "auto" else language,
        beam_size=5,
        word_timestamps=True,
    )

    transcript_segments = []
    for seg in segments:
        transcript_segments.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip(),
            "words": [{"word": w.word, "start": w.start, "end": w.end}
                      for w in (seg.words or [])]
        })

    return {
        "language": info.language,
        "duration": info.duration,
        "segments": transcript_segments,
        "full_text": " ".join(s["text"] for s in transcript_segments)
    }
```

### Step 3: Generate Markdown Output
```markdown
# Transcription Report

**File**: meeting_recording.mp3
**Duration**: 45:32
**Language**: English (detected)
**Transcribed**: 2026-03-08

---

## Executive Summary
[2–3 sentence summary of key points]

## Full Transcript

**[00:00]** Welcome everyone to our sprint planning session...
**[01:23]** Today we'll cover three main topics...

---

## Key Action Items
- [ ] Complete StageSense coach mode by Friday
- [ ] Setup SSE streaming endpoint

## Topics Discussed
1. StageSense architecture review (0:00–15:30)
2. Sprint priorities (15:30–35:00)
3. Demo prep (35:00–45:32)
```

### Step 4: Speaker Diarization (Optional)
```python
from pyannote.audio import Pipeline

def diarize(audio_path: str, hf_token: str) -> list[dict]:
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token
    )
    diarization = pipeline(audio_path)

    speakers = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speakers.append({
            "speaker": speaker,
            "start": turn.start,
            "end": turn.end,
        })
    return speakers
```

---

## Quick Install
```bash
pip install faster-whisper  # Fast CPU/GPU transcription
pip install pyannote.audio  # Speaker diarization (optional)
```

## When to Use
Use this skill to transcribe audio files, generate meeting notes, or produce timestamped transcripts for any audio/video content.
