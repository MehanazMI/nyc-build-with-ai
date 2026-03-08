---
name: pydantic-models-py
description: Create Pydantic models following the multi-model pattern for clean API contracts. Covers Base/Create/Update/Response/InDB patterns, camelCase aliases, and FastAPI integration.
---

# Pydantic Models

Create Pydantic models following the multi-model pattern for clean API contracts.

## Quick Start

Use the multi-model pattern for every resource:

- `Base` — shared fields
- `Create` — fields required at creation (POST body)
- `Update` — all fields optional (PATCH body)
- `Response` — fields returned to client
- `InDB` — adds `doc_type` for DB storage

---

## Multi-Model Pattern

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

# 1. Base — shared fields
class AnalysisSessionBase(BaseModel):
    mode: str = Field(..., description="'coach' or 'room_read'")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

# 2. Create — POST body
class AnalysisSessionCreate(AnalysisSessionBase):
    user_id: str

# 3. Update — PATCH body (all optional)
class AnalysisSessionUpdate(BaseModel):
    """All fields optional for PATCH requests."""
    mode: Optional[str] = None
    status: Optional[str] = None

# 4. Response — returned to client
class AnalysisSessionResponse(AnalysisSessionBase):
    id: str
    created_at: datetime
    status: str

    class Config:
        from_attributes = True  # SQLAlchemy compatibility

# 5. InDB — includes doc_type for Cosmos/Firestore
class AnalysisSessionInDB(AnalysisSessionResponse):
    doc_type: str = "analysis_session"
```

---

## camelCase Aliases (Frontend-Friendly)

```python
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    workspace_id: str = Field(..., alias="workspaceId")
    created_at: datetime = Field(..., alias="createdAt")
    session_id: str = Field(..., alias="sessionId")

    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase
```

---

## FastAPI Integration

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/sessions/", response_model=AnalysisSessionResponse, status_code=201)
async def create_session(payload: AnalysisSessionCreate) -> AnalysisSessionResponse:
    db_obj = AnalysisSessionInDB(**payload.model_dump(), id=str(uuid.uuid4()), ...)
    await db.save(db_obj)
    return AnalysisSessionResponse(**db_obj.model_dump())
```

---

## Validation Patterns

```python
from pydantic import field_validator, model_validator

class AnalysisConfig(BaseModel):
    mode: str
    confidence_threshold: float = Field(ge=0.0, le=1.0, default=0.7)
    max_duration_seconds: int = Field(gt=0, le=3600, default=300)

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        if v not in ("coach", "room_read"):
            raise ValueError("mode must be 'coach' or 'room_read'")
        return v
```

---

## Integration Steps
1. Create models in `app/models/` (one file per resource)
2. Export from `app/models/__init__.py`
3. Add corresponding TypeScript types for frontend

## When to Use
Use this skill when defining API contracts, database schemas, or data validation logic in Python FastAPI projects.
