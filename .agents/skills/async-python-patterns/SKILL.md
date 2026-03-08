---
name: async-python-patterns
description: Comprehensive guidance for implementing asynchronous Python applications using asyncio, concurrent programming patterns, and async/await for building high-performance, non-blocking systems.
---

# Async Python Patterns

## Use This Skill When
- Building async web APIs (FastAPI, aiohttp, Sanic)
- Implementing concurrent I/O operations (database, file, network)
- Creating web scrapers with concurrent requests
- Developing real-time applications (WebSocket servers, chat systems)
- Processing multiple independent tasks simultaneously
- Building microservices with async communication
- Optimizing I/O-bound workloads
- Implementing async background tasks and queues

## Do Not Use When
- The workload is CPU-bound with minimal I/O
- A simple synchronous script is sufficient
- The runtime environment cannot support asyncio/event loop usage

---

## Instructions
- Clarify workload characteristics (I/O vs CPU), targets, and runtime constraints
- Pick concurrency patterns (tasks, gather, queues, pools) with cancellation rules
- Add timeouts, backpressure, and structured error handling
- Include testing and debugging guidance for async code paths

---

## Core Patterns

### Task Gathering (Parallel I/O)
```python
import asyncio

async def fetch_all(urls: list[str]) -> list[dict]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    return [r.json() for r in responses if not isinstance(r, Exception)]
```

### Producer-Consumer with asyncio.Queue
```python
async def producer(queue: asyncio.Queue):
    while True:
        item = await generate_item()
        await queue.put(item)

async def consumer(queue: asyncio.Queue):
    while True:
        item = await queue.get()
        await process_item(item)
        queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=100)  # backpressure
    await asyncio.gather(producer(queue), consumer(queue))
```

### Timeouts and Cancellation
```python
async def safe_operation(coro, timeout: float = 30.0):
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.error("Operation timed out")
        return None
    except asyncio.CancelledError:
        logger.info("Operation cancelled — cleanup if needed")
        raise  # Always re-raise CancelledError
```

### Background Tasks
```python
class TaskManager:
    def __init__(self):
        self._tasks: set[asyncio.Task] = set()

    def spawn(self, coro) -> asyncio.Task:
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def shutdown(self):
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
```

### Async Context Manager (Resource Management)
```python
class AsyncConnection:
    async def __aenter__(self):
        self.conn = await open_connection()
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()

# Usage
async with AsyncConnection() as conn:
    await conn.query("SELECT 1")
```

### Streaming Async Generator
```python
async def stream_audio_chunks(websocket) -> AsyncGenerator[bytes, None]:
    """Stream audio chunks from WebSocket."""
    async for message in websocket.iter_bytes():
        yield message

# Consumer
async for chunk in stream_audio_chunks(ws):
    await transcriber.send_audio(chunk)
```

### Rate Limiting with Semaphore
```python
async def rate_limited_fetch(urls: list[str], concurrency: int = 10):
    semaphore = asyncio.Semaphore(concurrency)

    async def fetch_one(url):
        async with semaphore:
            async with httpx.AsyncClient() as client:
                return await client.get(url)

    return await asyncio.gather(*[fetch_one(u) for u in urls])
```

---

## Common Gotchas

| Gotcha | Fix |
|--------|-----|
| Sync code blocking event loop | Use `asyncio.to_thread()` for CPU-bound work |
| `CancelledError` swallowed | Always re-raise `CancelledError` |
| Event loop already running (Jupyter) | Use `nest_asyncio` or `asyncio.run()` in a subprocess |
| Tasks GC'd before completion | Keep references; use `TaskManager` pattern above |
| Unbounded queue causing OOM | Set `maxsize` on `asyncio.Queue` |
| `asyncio.sleep(0)` for yielding | Use to yield control back to the event loop intentionally |

---

## Testing Async Code
```python
import pytest

@pytest.mark.asyncio
async def test_my_async_function():
    result = await my_async_function()
    assert result == expected
```

## When to Use
Use this skill for all async Python work: concurrent I/O, WebSockets, background tasks, streaming generators, and async resource management.
