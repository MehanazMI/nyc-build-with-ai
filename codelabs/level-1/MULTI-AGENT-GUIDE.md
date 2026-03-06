# 🤖 Multi-Agent Systems for Hackathon

## What You Learned from Level 1

**Multi-agent systems** = Multiple specialized AI agents working together to solve complex problems.

### Key Concepts

#### 1. **Agent Specialization**
Each agent has a specific role:
- **Vision Agent**: Analyzes images/video
- **Conversation Agent**: Natural dialogue
- **Planner Agent**: Strategic thinking
- **Research Agent**: Information analysis

#### 2. **Orchestration Patterns**

**Pipeline (Sequential)**
```
Vision → Planner → Conversation → Result
```
Each agent processes in order, passing context forward.

**Parallel Processing**
```
     ┌─ Vision ──┐
Task ┼─ Audio  ──┼→ Coordinator → Result
     └─ Text  ──┘
```
Multiple agents work simultaneously, results combined.

**Hub-and-Spoke**
```
         Coordinator
         /    |    \
    Vision  Audio  Text
```
Central coordinator delegates to specialists.

#### 3. **Context Sharing**
Agents share information:
```python
context = {
    "vision_analysis": "Student is solving algebra",
    "detected_emotion": "frustrated",
    "topic": "quadratic equations"
}
```

---

## Applying to Your Hackathon Project

### Example: Homework Tutor (Live Agent)

**Agent Architecture:**
```
1. Vision Agent → Analyzes homework photo
2. Subject Agent → Identifies topic & difficulty
3. Planner Agent → Creates teaching strategy
4. Conversation Agent → Delivers friendly explanation
```

**Code Pattern:**
```python
orchestrator = MultiAgentOrchestrator()
orchestrator.register_agent("vision", VisionAgent())
orchestrator.register_agent("tutor", TutorAgent())

# Pipeline
tasks = [
    ("vision", "Analyze homework problem"),
    ("tutor", "Explain solution step-by-step")
]

results = orchestrator.run_pipeline(tasks)
```

### Example: Accessibility Assistant

**Agent Architecture:**
```
Vision Agent → Analyzes scene
         ↓
Navigation Agent → Plans safe route
         ↓
Voice Agent → Provides audio guidance
```

### Example: Visual Translator

**Agent Architecture:**
```
Vision Agent → Detects text in image
         ↓
Translation Agent → Translates text
         ↓
Context Agent → Adds cultural context
         ↓
Voice Agent → Speaks translation
```

---

## Implementation Guide

### Step 1: Define Your Agents

```python
class HomeworkVisionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Homework Analyzer",
            role="Visual Problem Recognition",
            system_instruction="""Analyze homework images:
            - Identify subject (math, science, etc.)
            - Extract problem text/equations
            - Detect student's work so far
            - Identify where they're stuck"""
        )

class TutorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="AI Tutor",
            role="Educational Guidance",
            system_instruction="""Be an encouraging tutor:
            - Explain concepts clearly
            - Use Socratic method (ask questions)
            - Provide hints, not full answers
            - Adapt to student's level"""
        )
```

### Step 2: Create Orchestrator

```python
orchestrator = MultiAgentOrchestrator()
orchestrator.register_agent("vision", HomeworkVisionAgent())
orchestrator.register_agent("tutor", TutorAgent())
```

### Step 3: Define Workflow

```python
# Sequential processing
tasks = [
    ("vision", "Analyze the homework problem"),
    ("tutor", "Help the student understand the solution")
]

results = orchestrator.run_pipeline(tasks)
```

---

## Best Practices for Hackathon

### 1. Start Simple
- Begin with 2-3 agents max
- Add complexity only if needed
- Focus on one clear use case

### 2. Clear Agent Roles
- Each agent should have ONE primary job
- Avoid overlap in responsibilities
- Use descriptive system instructions

### 3. Context is Key
```python
# Good: Pass relevant context
context = {
    "user_level": "beginner",
    "previous_answer": "x = 5",
    "current_problem": "2x + 3 = 13"
}

# Bad: Pass everything
context = entire_conversation_history  # Too much!
```

### 4. Error Handling
```python
try:
    result = agent.process(task)
except Exception as e:
    result = "I'm having trouble. Can you try again?"
```

### 5. Demo Strategy
- Show agent collaboration visually
- Print what each agent is doing
- Highlight how they work together

---

## Example Output Structure

```
🚀 MULTI-AGENT PIPELINE STARTED
======================================================================

🤖 Vision Analyst (Visual Understanding) processing...

📋 Result from Vision Analyst:
----------------------------------------------------------------------
Scene Overview: The image shows a math textbook page with a 
handwritten problem: "Solve for x: 2x + 5 = 15"
Subject: Algebra - Linear equations
Student Progress: Problem statement written, no solution attempts yet

🤖 AI Tutor (Educational Guidance) processing...

📋 Result from AI Tutor:
----------------------------------------------------------------------
Great! I see you're working on solving linear equations. Let's think
through this step by step:

1. What's our goal? We want x by itself on one side.
2. What's getting in the way? The +5 and the ×2
3. What should we do first? 

Hint: Think about the order of operations - what was done LAST to x?

✅ PIPELINE COMPLETE
======================================================================
```

---

## Quick Reference Code

### Basic Agent
```python
from hackathon_agents import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="My Agent",
            role="Specialized Task",
            system_instruction="Your detailed instructions"
        )
```

### Vision Agent
```python
from hackathon_agents import VisionAnalystAgent

vision = VisionAnalystAgent()
result = vision.analyze_image("photo.jpg", "What's in this image?")
```

### Orchestrator
```python
from hackathon_agents import MultiAgentOrchestrator

orch = MultiAgentOrchestrator()
orch.register_agent("id1", agent1)
orch.register_agent("id2", agent2)

results = orch.run_pipeline([
    ("id1", "Task for agent 1"),
    ("id2", "Task for agent 2")
])
```

---

## Testing Your System

### Run the Demo
```powershell
cd codelabs\level-1
python hackathon_agents.py
```

### Customize for Your Project
1. Copy `hackathon_agents.py` to your project folder
2. Modify agent classes for your use case
3. Adjust system instructions
4. Test with real scenarios

---

## Debugging Tips

### Agent Not Working?
- Check system instructions (be specific)
- Verify API key in .env
- Print intermediate results
- Test agents individually first

### Context Not Flowing?
- Verify shared_context is updated
- Check agent can access previous results
- Print context at each step

### Rate Limits?
- Use `gemini-2.0-flash-exp` (faster)
- Cache expensive operations
- Combine multiple steps when possible
- Wait between requests

---

## Resources

### Code Files
- `hackathon_agents.py` - Multi-agent framework
- `multi_agent.py` - Original Level 1 example
- Level 3 files - Integration with live features

### Documentation
- This guide - Multi-agent concepts
- `HACKATHON-IDEAS.md` - Project ideas using agents
- `HACKATHON-TRACKS.md` - Track requirements

---

## Next Steps

1. ✅ **Understand** multi-agent patterns (you're here!)
2. 🎯 **Choose** your hackathon project idea
3. 🔨 **Design** your agent architecture
4. 💻 **Build** your agents using the template
5. 🎭 **Demo** agent collaboration
6. 🏆 **Win** the hackathon!

**You're ready to build amazing multi-agent Live Agent projects!**
