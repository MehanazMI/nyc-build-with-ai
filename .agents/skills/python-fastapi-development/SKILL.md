---
name: python-fastapi-development
description: Specialized workflow for building production-ready Python backends with FastAPI, featuring async patterns, SQLAlchemy ORM, Pydantic validation, and comprehensive API patterns.
---

# Python/FastAPI Development Workflow

## Overview
Specialized workflow for building production-ready Python backends with FastAPI, featuring async patterns, SQLAlchemy ORM, Pydantic validation, and comprehensive API patterns.

## When to Use
- Building new REST APIs with FastAPI
- Creating async Python backends
- Implementing database integration with SQLAlchemy
- Setting up API authentication
- Developing microservices

---

## Workflow Phases

### Phase 1: Project Setup
1. Set up Python environment with `uv` or `poetry`
2. Create project structure
3. Configure FastAPI app with lifespan events
4. Set up structured logging
5. Configure environment variables with Pydantic Settings

**Quick scaffold:**
```bash
uv init my-api && cd my-api
uv add fastapi uvicorn[standard] pydantic-settings httpx
uv add --dev pytest pytest-asyncio pytest-cov
```

### Phase 2: Application Structure
```
app/
├── main.py           # FastAPI app + lifespan
├── config.py         # Pydantic Settings
├── models/           # Pydantic models (Base, Create, Update, Response)
├── routers/          # API route handlers (one file per resource)
├── services/         # Business logic layer
├── dependencies.py   # FastAPI Depends() factories
└── middleware.py     # CORS, logging, auth middleware
```

### Phase 3: API Routes
```python
# routers/analysis.py
from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/", response_model=AnalysisResponse, status_code=201)
async def create_analysis(
    payload: AnalysisCreate,
    user = Depends(get_current_user),
):
    return await analysis_service.create(payload, user_id=user.id)
```

### Phase 4: Authentication (JWT)
```python
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return await user_service.get_by_id(user_id)
```

### Phase 5: Error Handling
```python
from fastapi import Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
```

### Phase 6: Testing
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_analysis(async_client: AsyncClient, auth_headers):
    response = await async_client.post(
        "/analysis/",
        json={"mode": "coach", "session_id": "test-123"},
        headers=auth_headers,
    )
    assert response.status_code == 201
```

### Phase 7: Deployment
```dockerfile
FROM python:3.12-slim
RUN pip install uv
COPY . .
RUN uv sync --frozen
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

---

## Quality Gates
- [ ] All endpoints have response_model and status_code defined
- [ ] Auth middleware covers all non-public endpoints
- [ ] Custom exception handlers return consistent JSON
- [ ] `pytest` passes with >80% coverage
- [ ] OpenAPI docs auto-generated at `/docs`
