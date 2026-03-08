---
name: agent-orchestration-multi-agent-optimize
description: AI-Powered Multi-Agent Performance Engineering Specialist. Optimize multi-agent systems through profiling, context window management, parallel execution, cost tracking, and latency reduction.
---

# Multi-Agent Optimization Toolkit

**Role**: AI-Powered Multi-Agent Performance Engineering Specialist

## Use This Skill When
- Profiling and optimizing multi-agent system performance
- Reducing token costs in multi-agent pipelines
- Improving latency in agent orchestration
- Debugging bottlenecks in parallel agent execution
- Context window management and optimization

---

## Core Capabilities
- Intelligent multi-agent coordination
- Performance profiling and bottleneck identification
- Adaptive optimization strategies
- Cross-domain performance optimization
- Cost and efficiency tracking

---

## 1. Multi-Agent Performance Profiling

**Profiling Strategy:**
1. Identify bottleneck agents (highest latency contributors)
2. Measure token usage per agent
3. Track tool call frequency and success rates
4. Monitor queue depths and wait times

```python
import time
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AgentTrace:
    agent_name: str
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    token_usage: int = 0
    tool_calls: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def latency_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return -1.0

class MultiAgentProfiler:
    def __init__(self):
        self.traces: dict[str, AgentTrace] = {}

    def start(self, agent_name: str) -> AgentTrace:
        trace = AgentTrace(agent_name=agent_name)
        self.traces[agent_name] = trace
        return trace

    def end(self, agent_name: str, token_usage: int = 0):
        if agent_name in self.traces:
            self.traces[agent_name].end_time = time.time()
            self.traces[agent_name].token_usage = token_usage

    def report(self) -> dict[str, Any]:
        return {
            "total_latency_ms": sum(t.latency_ms for t in self.traces.values()),
            "total_tokens": sum(t.token_usage for t in self.traces.values()),
            "bottleneck": max(self.traces.values(), key=lambda t: t.latency_ms).agent_name,
            "agents": {k: {"latency_ms": v.latency_ms, "tokens": v.token_usage}
                      for k, v in self.traces.items()}
        }
```

---

## 2. Context Window Optimization

**Optimization Techniques:**
- Summarize agent outputs before passing to next agent
- Use structured extraction (only pass needed fields)
- Apply context compression for long histories
- Delete stale state keys aggressively

```python
async def compress_context(agent_state: dict, max_tokens: int = 4000) -> dict:
    """Compress agent state to fit within token budget."""
    # Remove verbose fields
    compressed = {k: v for k, v in agent_state.items()
                  if k not in ("raw_response", "debug_info", "intermediate_steps")}

    # Summarize long text values
    for key, value in compressed.items():
        if isinstance(value, str) and len(value) > 1000:
            compressed[key] = await summarize(value, max_tokens=200)

    return compressed
```

---

## 3. Parallel Execution Optimization

**Key Strategies:**
- Use `asyncio.gather()` for truly independent agents
- Avoid shared mutable state between parallel agents
- Each parallel agent must have its **own** tool instances (never shared singletons)
- Set timeouts on each parallel agent to prevent blocking

```python
import asyncio

async def run_parallel_agents(agents: list, task: str) -> list:
    """Run agents in parallel with timeout protection."""
    tasks = [
        asyncio.wait_for(agent.run(task), timeout=60.0)
        for agent in agents
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]
```

---

## 4. Cost Optimization

**LLM Cost Management:**
- Route simple subtasks to cheaper/faster models (e.g., `gemini-3-flash-preview`)
- Route complex reasoning to premium models (e.g., `gemini-3-pro-preview`)
- Cache repeated agent calls with identical inputs
- Use structured output to reduce output token waste

```python
def select_model_for_task(task_complexity: str) -> str:
    model_map = {
        "simple": "gemini-3-flash-preview",    # Fast + cheap
        "medium": "gemini-3-flash-preview",
        "complex": "gemini-3-pro-preview",     # Best quality
    }
    return model_map.get(task_complexity, "gemini-3-flash-preview")
```

---

## 5. Latency Reduction

- **Prefetch** data before agents need it (use `before_agent_callback`)
- **Pipeline** agents instead of waiting for all to complete
- **Streaming**: Return first result to user while other agents run
- **Model selection**: Faster models reduce latency more than more parallelism

---

## 6. Quality vs. Speed Tradeoffs

| Optimization | Latency | Cost | Quality |
|---|---|---|---|
| Faster model | ✅ Better | ✅ Better | ⚠️ Slight loss |
| More parallelism | ✅ Better | ❌ Higher | = Same |
| Context compression | ✅ Better | ✅ Better | ⚠️ Possible loss |
| Response caching | ✅ Better | ✅ Better | ⚠️ Staleness risk |

## When to Use
Use this skill when multi-agent pipelines are too slow, too expensive, or bottlenecked. Profile first, then optimize the highest-impact component.
