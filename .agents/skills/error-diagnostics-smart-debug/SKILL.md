---
name: error-diagnostics-smart-debug
description: Expert AI-assisted debugging specialist. Systematic 10-step debugging workflow covering triage, observability, hypothesis generation, root cause analysis, fix implementation, and prevention.
---

# Error Diagnostics — Smart Debug

**Role**: Expert AI-Assisted Debugging Specialist

## Use This Skill When
- Diagnosing unexpected errors or exceptions
- Debugging async pipelines (FastAPI, asyncio, WebSockets)
- Investigating intermittent production failures
- Performing root cause analysis

---

## 10-Step Debug Workflow

### 1. Initial Triage
Parse the error for:
- Error messages / stack traces
- Reproduction steps
- Affected components / services
- Environment (dev / staging / production)
- Failure pattern: intermittent vs. consistent

Generate **3–5 ranked hypotheses** with probability scores.

### 2. Observability Data Collection
Gather from:
- Error tracking (Sentry, Rollbar)
- APM metrics (DataDog, New Relic)
- Distributed traces (Jaeger, Zipkin)
- Log aggregation (ELK, Loki, CloudWatch)

Query for:
- Error frequency / trends
- Affected user cohorts
- Deployment timeline correlation

### 3. Hypothesis Generation
For each hypothesis include:
- **Probability score** (0–100%)
- Supporting evidence from logs / traces
- **Falsification criteria** — how to prove it wrong
- Testing approach

Common categories:
- Logic errors (race conditions, null handling)
- State management (stale cache, incorrect transitions)
- Integration failures (API changes, timeouts, auth)
- Resource exhaustion (memory leaks, connection pools)
- Configuration drift (env vars, feature flags)

### 4. Strategy Selection
| Issue Type | Strategy |
|---|---|
| Reproducible locally | Interactive debugging (step-through) |
| Production only | Observability-driven (Sentry/DataDog) |
| Complex state | Time-travel debugging (Redux DevTools, rr) |
| Intermittent under load | Chaos engineering |
| Affects small % of cases | Statistical / delta debugging |

### 5. Intelligent Instrumentation
Add breakpoints / logpoints at:
- Entry points to affected functionality
- Decision nodes where behavior diverges
- State mutation points
- External integration boundaries (API calls, DB queries)
- Error handling paths

```python
import logging
logger = logging.getLogger(__name__)

async def problematic_function(data):
    logger.debug("Entering problematic_function", extra={"data_keys": list(data.keys())})
    try:
        result = await process(data)
        logger.debug("process() succeeded", extra={"result_type": type(result).__name__})
        return result
    except Exception as e:
        logger.error("process() failed", exc_info=True, extra={"data": data})
        raise
```

### 6. Async-Specific Techniques (Python)
```python
import asyncio

# Detect event loop blocking
async def detect_blocking():
    loop = asyncio.get_event_loop()
    slow_threshold = 0.1  # 100ms

    def slow_callback_detector(duration):
        if duration > slow_threshold:
            logger.warning(f"Slow callback: {duration:.3f}s")

    loop.slow_callback_duration = slow_threshold

# Dump all running tasks (for debugging deadlocks)
def dump_tasks():
    for task in asyncio.all_tasks():
        print(f"Task: {task.get_name()} — {task.get_coro().__name__}")
        task.print_stack()
```

### 7. Root Cause Analysis
Reconstruct:
- Full execution path
- Variable state at decision points
- External dependency interaction timeline
- Race condition windows (concurrent task timing)

### 8. Fix Implementation
Every fix must include:
- Code change
- Impact assessment (what else could break?)
- Risk level (low / medium / high)
- Test coverage requirements
- Rollback strategy

### 9. Validation
- Run `pytest` suite
- Performance comparison (baseline vs. fix)
- Test in same environment where bug was found
- Verify no new edge cases

### 10. Prevention
- Generate regression tests using the bug's reproduction steps
- Add monitoring / alerts for similar future failures
- Document root cause and fix in runbook

---

## Common Async Python Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| `CancelledError` swallowed | Silent task death | Always re-raise `CancelledError` |
| Sync blocking in async | Event loop freezes | Use `asyncio.to_thread()` |
| Task GC'd early | Task disappears mid-run | Keep reference in a set |
| Shared state between parallel tasks | Race condition | Use `asyncio.Lock()` |
| `await` inside non-async callback | `SyntaxError` or no-op | Wrap in `asyncio.create_task()` |

## When to Use
Use this skill for any systematic debugging effort — errors, performance regressions, intermittent failures, or async pipeline issues.
