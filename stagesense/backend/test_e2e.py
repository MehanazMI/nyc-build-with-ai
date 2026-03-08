"""
Quick end-to-end test for StageSense:
1. Connects WebSocket to /ws
2. Sends 10 seconds of silence (PCM 16kHz) as audio
3. Watches SSE /stream for score_update events
4. Prints any scores received
"""
import asyncio
import json
import struct
import aiohttp
import websockets

BACKEND = "http://localhost:8080"
WS_URL = "ws://localhost:8080/ws"
SSE_URL = "http://localhost:8080/stream"

# 100ms of silence at 16kHz = 1600 samples * 2 bytes = 3200 bytes
SILENCE_CHUNK = struct.pack("<" + "h" * 1600, *([0] * 1600))


async def watch_sse(scores_received: list):
    """Poll SSE stream and collect score_update events."""
    async with aiohttp.ClientSession() as session:
        async with session.get(SSE_URL) as resp:
            async for line in resp.content:
                text = line.decode().strip()
                if text.startswith("data:"):
                    try:
                        data = json.loads(text[5:].strip())
                        scores_received.append(data)
                        print(f"  📊 SCORE: {json.dumps(data, indent=2)}")
                    except:
                        pass


async def run_ws_session():
    """Connect WebSocket, send audio for 25s, then close."""
    print(f"🔌 Connecting WebSocket to {WS_URL}...")
    try:
        async with websockets.connect(WS_URL) as ws:
            print("✅ WebSocket connected — sending audio...")
            # Send silence for 25 seconds (250 chunks × 100ms)
            for i in range(250):
                try:
                    await ws.send(SILENCE_CHUNK)
                except Exception as e:
                    print(f"  ⚡ WS send ended: {type(e).__name__}")
                    break
                await asyncio.sleep(0.1)
                if i % 30 == 0:
                    print(f"  🎙 Sent {i/10:.0f}s of audio...")
            print("⏹  Audio send complete — closing")
    except Exception as e:
        print(f"  ⚡ WS session ended: {type(e).__name__}: {str(e)[:60]}")


async def main():
    scores = []

    # Start SSE watcher in background
    sse_task = asyncio.create_task(watch_sse(scores))

    # Wait a moment for SSE to connect
    await asyncio.sleep(0.5)

    # Run WebSocket session
    await run_ws_session()

    # Wait a couple more seconds for final scores
    await asyncio.sleep(3)

    sse_task.cancel()
    try:
        await sse_task
    except asyncio.CancelledError:
        pass

    print(f"\n{'='*50}")
    print(f"✅ Test complete — received {len(scores)} score update(s)")
    if scores:
        print(f"Last score: {json.dumps(scores[-1], indent=2)}")
    else:
        print("❌ No scores received — check server logs")


if __name__ == "__main__":
    asyncio.run(main())
