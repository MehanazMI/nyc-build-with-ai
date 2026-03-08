---
name: fastapi-templates
description: Production-ready FastAPI project structures with async patterns, dependency injection, middleware, and best practices for building high-performance APIs.
---

# FastAPI Project Templates

Production-ready FastAPI project structures with async patterns, dependency injection, middleware, and best practices for building high-performance APIs.

## Use This Skill When
- Starting new FastAPI projects from scratch
- Implementing async REST APIs with Python
- Building high-performance web services and microservices
- Creating async applications with PostgreSQL, MongoDB
- Setting up API projects with proper structure and testing

---

## Project Structure Template

```
my-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + lifespan
│   ├── config.py            # Pydantic Settings
│   ├── dependencies.py      # Shared Depends() factories
│   ├── middleware.py        # CORS, logging, auth
│   ├── models/
│   │   ├── __init__.py
│   │   └── session.py       # Pydantic models (Base/Create/Update/Response)
│   ├── routers/
│   │   ├── __init__.py
│   │   └── sessions.py      # Route handlers
│   └── services/
│       └── session_service.py
├── tests/
│   ├── conftest.py
│   └── test_sessions.py
├── pyproject.toml
└── Dockerfile
```

---

## main.py Template

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import sessions, analysis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.app_name,
    description="API description",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}
```

---

## config.py Template

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "My FastAPI App"
    debug: bool = False
    allowed_origins: list[str] = ["http://localhost:3000"]

    # API keys
    google_cloud_project: str = ""
    google_genai_use_vertexai: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

---

## Router Template

```python
from fastapi import APIRouter, Depends, HTTPException, status
from ..models.session import SessionCreate, SessionResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("/", response_model=list[SessionResponse])
async def list_sessions(
    skip: int = 0,
    limit: int = 20,
    user = Depends(get_current_user),
):
    return await session_service.list(user_id=user.id, skip=skip, limit=limit)

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SessionCreate,
    user = Depends(get_current_user),
):
    return await session_service.create(payload, user_id=user.id)

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, user = Depends(get_current_user)):
    session = await session_service.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
```

---

## conftest.py Testing Template

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}
```

---

## When to Use
Use this skill when scaffolding new FastAPI services or needing a production-ready template with consistent structure and patterns.
