---
name: fastapi-pro
description: Expert FastAPI developer specializing in high-performance, async-first API development. Masters modern Python web development with FastAPI, focusing on production-ready microservices, scalable architectures, and cutting-edge async patterns.
---

# FastAPI Pro

## Use This Skill When
- Working on FastAPI development tasks
- Needing guidance, best practices, or checklists for FastAPI
- Building async APIs, WebSocket endpoints, SSE streaming, or microservices

## Do Not Use When
- The task is unrelated to FastAPI
- You need a different backend framework

---

## Core Capabilities

### Core FastAPI
- FastAPI 0.100+ features with `Annotated` types and modern dependency injection
- Async/await patterns for high-concurrency applications
- Pydantic V2 for data validation and serialization
- Automatic OpenAPI/Swagger documentation generation
- WebSocket support for real-time communication
- Background tasks with BackgroundTasks and task queues
- File uploads and streaming responses
- Custom middleware and request/response interceptors

### API Design & Architecture
- RESTful API design principles
- API versioning strategies
- Rate limiting and throttling
- Circuit breaker pattern
- Event-driven architecture with message queues
- CQRS and Event Sourcing patterns
- Microservices architecture

### Authentication & Security
- OAuth2 with JWT tokens (`python-jose`, `pyjwt`)
- Social authentication (Google, GitHub, etc.)
- API key authentication
- Role-based access control (RBAC)
- CORS configuration and security headers
- Rate limiting per user/IP

### Performance Optimization
- Async programming best practices
- Connection pooling (database, HTTP clients)
- Response caching with Redis or Memcached
- Pagination and cursor-based pagination
- Response compression (gzip, brotli)

### Integration Patterns
- Message queues (RabbitMQ, Kafka, Redis Pub/Sub)
- Task queues with Celery or Dramatiq
- External API integration with `httpx`
- **Server-Sent Events (SSE)**
- Webhook implementation
- File storage (S3, MinIO, local)

### Advanced Features
- Dependency injection with advanced patterns
- Lifespan events for startup/shutdown
- Custom exception handlers
- Request context and state management
- Content negotiation

---

## SSE Streaming Pattern (Key for StageSense)

```python
from sse_starlette.sse import EventSourceResponse
import asyncio, json

@app.get("/stream")
async def stream(request: Request):
    async def generator():
        while True:
            if await request.is_disconnected():
                break
            yield {"event": "update", "data": json.dumps({"status": "coaching"})}
            await asyncio.sleep(0.5)
    return EventSourceResponse(generator())
```

## WebSocket Pattern

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            # process audio/video frame
            result = await process_frame(data)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        await cleanup(session_id)
```

## Lifespan Events (Startup/Shutdown)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await start_kafka_consumer()
    yield
    # Shutdown
    await close_db()
    await stop_kafka_consumer()

app = FastAPI(lifespan=lifespan)
```

## When to Use
Use this skill for any FastAPI development: routing, middleware, WebSocket, SSE, dependency injection, security, or performance optimization.
