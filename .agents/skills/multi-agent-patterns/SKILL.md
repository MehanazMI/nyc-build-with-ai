---
name: multi-agent-patterns
description: Multi-agent architecture patterns covering supervisor/orchestrator, peer-to-peer/swarm, and hierarchical designs. Includes context isolation principles, consensus mechanisms, failure mode mitigation, and the telephone game fix.
---

# Multi-Agent Architecture Patterns

## When to Activate
- Single-agent context limits constrain task complexity
- Tasks decompose naturally into parallel subtasks
- Different subtasks require different tool sets or system prompts
- Building systems that handle multiple domains simultaneously
- Scaling agent capabilities beyond single-context limits
- Designing production agent systems with multiple specialized components

## Core Concepts
Multi-agent systems address single-agent context limitations through distribution. Three dominant patterns exist:
1. **Supervisor/Orchestrator** — centralized control
2. **Peer-to-peer/Swarm** — flexible handoffs
3. **Hierarchical** — layered abstraction

**Critical design principle**: Context isolation — sub-agents exist primarily to **partition context** rather than simulate organizational roles.

---

## Pattern 1: Supervisor/Orchestrator (Centralized Control)

```
User Query → Supervisor → [Specialist A, Specialist B, Specialist C]
                       → Aggregation → Final Output
```

**When to use**: Complex tasks with clear decomposition, tasks requiring domain coordination.

**Advantages**: Strict workflow control, easier human-in-the-loop, adherence to predefined plans.

**Disadvantages**: Supervisor context becomes bottleneck; "telephone game" problem.

### ⚠️ The Telephone Game Problem

LangGraph benchmarks: Supervisor architectures performed **50% worse** due to supervisors paraphrasing sub-agent responses incorrectly.

**Fix — Add a `forward_message` tool:**
```python
def forward_message(message: str, to_user: bool = True):
    """
    Forward sub-agent response directly to user without supervisor synthesis.
    Use when: sub-agent response is final and complete, or format must be preserved.
    """
    if to_user:
        return {"type": "direct_response", "content": message}
    return {"type": "supervisor_input", "content": message}
```

---

## Pattern 2: Peer-to-Peer / Swarm (No Central Control)

```python
def transfer_to_agent_b():
    return agent_b  # Handoff via function return

agent_a = Agent(
    name="Agent A",
    functions=[transfer_to_agent_b]
)
```

**When to use**: Flexible exploration tasks, emergent requirements that defy upfront decomposition.

**Advantages**: No single point of failure, scales for breadth-first exploration, emergent problem-solving.

**Disadvantages**: Coordination complexity grows with agent count; risk of divergence.

---

## Pattern 3: Hierarchical

```
Strategy Layer (Goal Definition)
    ↓
Planning Layer (Task Decomposition)
    ↓
Execution Layer (Atomic Tasks)
```

**When to use**: Large-scale projects with clear hierarchical structure, enterprise workflows with management layers.

---

## Token Economics Reality

Research on BrowseComp evaluation found **3 factors explain 95% of performance variance**:
1. Token usage (80% of variance)
2. Number of tool calls
3. Model choice

> **Key insight**: Upgrading to a better model often gives larger gains than doubling token budgets. Use model selection AND multi-agent architecture as complementary strategies.

---

## The Parallelization Argument

Sequential single agent:
- Task A (10s) → Task B (10s) → Task C (10s) = **30s total**

Parallel multi-agent:
- Task A | Task B | Task C = **~10s total** (longest task duration)

---

## Context Isolation as Design Principle

| Anti-Pattern | Better Approach |
|---|---|
| Monolithic agent reads all docs | Specialized agents each read their domain docs |
| Single agent for all tasks | Route to specialized agents with lean context |
| Supervisor synthesizes all results | Use `forward_message` for direct pass-through |

---

## Failure Modes and Mitigations

| Failure Mode | Mitigation |
|---|---|
| Supervisor bottleneck | Implement direct response pass-through |
| Agent divergence | Define convergence constraints / max hops |
| Telephone game errors | Add `forward_message` tool |
| Error propagation | Isolate failures per agent; use fallbacks |
| Context poisoning | Use fresh contexts for each sub-agent |

---

## Framework Considerations

- **Google ADK**: `ParallelAgent`, `SequentialAgent`, `Agent` with `sub_agents`
- **LangGraph**: State graph with supervisors and workers
- **OpenAI Swarm**: Lightweight handoffs via function returns

## Related Skills
`google-adk-agents`, `ai-agents-architect`, `agent-orchestration-multi-agent-optimize`

## When to Use
Use this skill when designing or debugging multi-agent systems, choosing orchestration patterns, or optimizing agent coordination.
