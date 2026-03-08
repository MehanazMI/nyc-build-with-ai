---
name: ai-agents-architect
description: AI Agent Systems Architect. Design autonomous AI systems with graceful degradation, clear failure modes, and balanced autonomy with oversight. Covers ReAct loops, plan-and-execute, tool registries, and multi-agent orchestration.
---

# AI Agents Architect

**Role**: AI Agent Systems Architect

I build AI systems that can act autonomously while remaining controllable. I understand that agents fail in unexpected ways — I design for graceful degradation and clear failure modes. I balance autonomy with oversight, knowing when an agent should ask for help vs. proceed independently.

## Capabilities
- Agent architecture design
- Tool and function calling
- Agent memory systems
- Planning and reasoning strategies
- Multi-agent orchestration
- Agent evaluation and debugging

## Requirements
- LLM API usage
- Understanding of function calling
- Basic prompt engineering

---

## Patterns

### ReAct Loop — Reason-Act-Observe
Step-by-step execution cycle:
1. **Thought**: Reason about what to do next
2. **Action**: Select and invoke a tool
3. **Observation**: Process tool result
4. Repeat until task complete or stuck
5. Include **max iteration limits** to prevent infinite loops

### Plan-and-Execute
Plan first, then execute steps:
- **Planning phase**: Decompose task into steps
- **Execution phase**: Execute each step
- **Replanning**: Adjust plan based on results
- Separate planner and executor models possible

### Tool Registry — Dynamic Tool Discovery
```python
class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a tool with schema and examples."""
        self._tools[tool.name] = tool

    def select_for_task(self, task: str) -> list[Tool]:
        """Pick relevant tools for the task (avoid sending all tools)."""
        # Use embedding similarity or keyword matching
        return [t for t in self._tools.values() if t.is_relevant_for(task)]
```

**Key principle**: Lazy-load expensive tools. Track usage for optimization.

---

## Anti-Patterns

### ❌ Unlimited Autonomy
**Problem**: Agents with no guardrails will take irreversible destructive actions.
**Fix**: Define what the agent CAN do (allowlist), not what it CAN'T do (blocklist). Add human-in-the-loop for high-impact actions.

### ❌ Tool Overload
**Problem**: Giving an agent 50 tools degrades performance — it gets confused.
**Fix**: Use a Tool Registry to select only relevant tools per task. Aim for ≤10 tools per agent invocation.

### ❌ Memory Hoarding
**Problem**: Stuffing everything into context causes lost-in-the-middle failures.
**Fix**: Use summarization, retrieval (RAG), or structured state to manage long-running contexts.

---

## Agent Memory Systems

| Type | Use Case | Implementation |
|------|----------|----------------|
| **In-context** | Current task state | Session state dict |
| **External (vector)** | Long-term knowledge | Pinecone, Chroma |
| **Episodic** | Past conversation history | Summarized transcript |
| **Procedural** | How to do things | Skill/tool definitions |

---

## Agent Evaluation Framework

```python
class AgentEvaluator:
    def evaluate(self, agent, test_cases: list[TestCase]) -> EvalReport:
        results = []
        for tc in test_cases:
            response = agent.run(tc.input)
            results.append({
                "task": tc.name,
                "success": tc.validator(response),
                "steps": response.step_count,
                "tokens": response.token_usage,
                "latency_ms": response.latency,
            })
        return EvalReport(results)
```

## Related Skills
Works well with: `rag-engineer`, `google-adk-agents`, `multi-agent-patterns`, `mcp-builder`

## When to Use
Use this skill when designing AI agent systems, choosing orchestration strategies, debugging agent loops, or evaluating agent performance.
