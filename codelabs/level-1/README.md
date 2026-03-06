# Level 1: Multi-Agent Systems - "Way Back Home"

## 🎯 Learning Objectives
- Understand multi-agent orchestration
- Learn agent-to-agent communication
- Implement specialized agents with distinct roles
- Coordinate agents to solve complex problems

## 📖 Tutorial Reference
Based on: https://codelabs.developers.google.com/way-back-home-level-1/instructions

## 🔧 What You'll Build
A multi-agent system where specialized agents work together:
- **Planner Agent**: Creates high-level strategies
- **Research Agent**: Gathers and analyzes information
- **Writer Agent**: Crafts compelling narratives
- **Coordinator**: Orchestrates agent interactions

## 🚀 Running the Code

```bash
cd codelabs/level-1
python multi_agent.py
```

## 📝 Key Concepts

### 1. Agent Specialization
Each agent has:
- Specific role and expertise
- Custom system instructions
- Unique capabilities

### 2. Agent Communication
- Sequential handoffs
- Shared context
- Result aggregation

### 3. Orchestration Patterns
- **Pipeline**: A → B → C (sequential)
- **Hub-and-Spoke**: Coordinator manages specialists
- **Peer-to-Peer**: Direct agent collaboration

## 🏗️ Architecture

```
         ┌─────────────┐
         │ Coordinator │
         └──────┬──────┘
                │
       ┌────────┼────────┐
       │        │        │
   ┌───▼───┐ ┌─▼──┐ ┌───▼────┐
   │Planner│ │Res.│ │ Writer │
   └───────┘ └────┘ └────────┘
```

## 🎨 Extensions
- Add more specialized agents (critic, fact-checker)
- Implement parallel agent execution
- Add memory/state management
- Create agent negotiation protocols

## 📚 Next Steps
After completing this level:
- [Level 3: Advanced Multimodal](../level-3/README.md)
- Build your hackathon project!
