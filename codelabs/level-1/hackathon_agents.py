#!/usr/bin/env python3
"""
Hackathon Multi-Agent System
Build specialized agents that work together for your Live Agent project
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class BaseAgent:
    """Base agent with core capabilities."""
    
    def __init__(self, name: str, role: str, system_instruction: str):
        """Initialize agent.
        
        Args:
            name: Agent's display name
            role: Agent's role description
            system_instruction: Detailed instructions for the agent
        """
        self.name = name
        self.role = role
        self.system_instruction = system_instruction
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-2.0-flash-exp'  # Faster model for hackathon
        
    def process(self, task: str, context: Optional[Dict] = None) -> str:
        """Process a task with optional context.
        
        Args:
            task: The task to perform
            context: Optional context dictionary from previous agents
            
        Returns:
            Agent's response
        """
        # Build prompt with context
        prompt = task
        if context:
            context_str = "\n\n".join([f"{k}: {v}" for k, v in context.items()])
            prompt = f"Context from previous agents:\n{context_str}\n\n{task}"
        
        print(f"\n🤖 {self.name} ({self.role}) processing...")
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7
                )
            )
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"


class VisionAnalystAgent(BaseAgent):
    """Agent specialized in visual analysis."""
    
    def __init__(self):
        super().__init__(
            name="Vision Analyst",
            role="Visual Understanding",
            system_instruction="""You are a Vision Analysis Expert.
            
Your role:
- Analyze images and identify key elements
- Describe scenes in detail (objects, people, setting, mood)
- Extract relevant information for decision-making
- Identify safety concerns or important details

Output format:
1. Scene Overview
2. Key Objects/People
3. Important Details
4. Recommendations

Be concise, accurate, and helpful."""
        )
    
    def analyze_image(self, image_path: str, question: str = "Describe this image") -> str:
        """Analyze an image with vision capabilities.
        
        Args:
            image_path: Path to image file
            question: Question to ask about the image
            
        Returns:
            Analysis result
        """
        from PIL import Image
        
        print(f"\n🤖 {self.name} analyzing image...")
        
        try:
            image = Image.open(image_path)
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[question, image],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.4
                )
            )
            return response.text
        except Exception as e:
            return f"Error analyzing image: {str(e)}"


class ConversationAgent(BaseAgent):
    """Agent specialized in natural conversation."""
    
    def __init__(self):
        super().__init__(
            name="Conversation Manager",
            role="Natural Dialogue",
            system_instruction="""You are a Friendly Conversation Manager.
            
Your role:
- Engage users in natural, helpful dialogue
- Ask clarifying questions when needed
- Provide clear, concise responses
- Adapt tone to user's needs (educational, professional, casual)
- Remember conversation context

Be warm, helpful, and conversational."""
        )
        self.conversation_history = []
    
    def chat(self, user_message: str, context: Optional[Dict] = None) -> str:
        """Have a conversation with context awareness.
        
        Args:
            user_message: User's message
            context: Additional context (e.g., from vision analysis)
            
        Returns:
            Agent's response
        """
        # Build context
        full_prompt = user_message
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            full_prompt = f"Available context:\n{context_str}\n\nUser: {user_message}"
        
        response = self.process(full_prompt)
        
        # Track history (simplified)
        self.conversation_history.append({
            "user": user_message,
            "agent": response
        })
        
        return response


class TaskPlannerAgent(BaseAgent):
    """Agent specialized in breaking down tasks."""
    
    def __init__(self):
        super().__init__(
            name="Task Planner",
            role="Strategic Planning",
            system_instruction="""You are a Strategic Task Planner.
            
Your role:
- Break complex goals into actionable steps
- Create clear, numbered action plans
- Identify dependencies and prerequisites
- Suggest realistic timelines

Output format:
1. Goal Summary
2. Step-by-step Plan (numbered)
3. Key Considerations
4. Success Metrics

Be practical and action-oriented."""
        )


class MultiAgentOrchestrator:
    """Coordinates multiple agents working together."""
    
    def __init__(self):
        """Initialize the orchestrator with agents."""
        self.agents = {}
        self.shared_context = {}
        
    def register_agent(self, agent_id: str, agent: BaseAgent):
        """Register an agent with the orchestrator.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: The agent instance
        """
        self.agents[agent_id] = agent
        print(f"✅ Registered: {agent.name}")
    
    def run_pipeline(self, tasks: List[tuple]) -> Dict:
        """Run agents in a pipeline (sequential).
        
        Args:
            tasks: List of (agent_id, task_description) tuples
            
        Returns:
            Dictionary with results from each agent
        """
        results = {}
        
        print("\n" + "="*70)
        print("🚀 MULTI-AGENT PIPELINE STARTED")
        print("="*70)
        
        for agent_id, task in tasks:
            if agent_id not in self.agents:
                results[agent_id] = f"Error: Agent '{agent_id}' not found"
                continue
            
            agent = self.agents[agent_id]
            
            # Execute task with shared context
            result = agent.process(task, self.shared_context)
            
            # Update shared context
            self.shared_context[agent.name] = result
            results[agent_id] = result
            
            print(f"\n📋 Result from {agent.name}:")
            print("-" * 70)
            print(result[:300] + "..." if len(result) > 300 else result)
        
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETE")
        print("="*70)
        
        return results


def demo_homework_tutor():
    """Demo: Homework Tutor using multi-agent system."""
    print("\n" + "="*70)
    print("📚 DEMO: AI Homework Tutor (Multi-Agent)")
    print("="*70)
    
    # Create orchestrator
    orchestrator = MultiAgentOrchestrator()
    
    # Register agents
    orchestrator.register_agent("vision", VisionAnalystAgent())
    orchestrator.register_agent("conversation", ConversationAgent())
    orchestrator.register_agent("planner", TaskPlannerAgent())
    
    # Example: Student takes photo of math homework
    print("\n📸 Student takes photo of homework problem...")
    print("🎯 Problem: How do I solve this algebra equation?")
    
    # Pipeline: Vision → Planning → Conversation
    tasks = [
        ("vision", "What mathematical problem is shown? Extract the equation and identify the topic."),
        ("planner", "Create a step-by-step plan to teach this concept to a high school student."),
        ("conversation", "Based on the analysis and plan, provide an encouraging, educational explanation to the student.")
    ]
    
    results = orchestrator.run_pipeline(tasks)
    
    print("\n" + "="*70)
    print("💡 This demonstrates how agents collaborate:")
    print("  1. Vision Agent: Understands the homework problem")
    print("  2. Planner Agent: Creates teaching strategy")
    print("  3. Conversation Agent: Delivers friendly explanation")
    print("="*70)


def demo_accessibility_assistant():
    """Demo: Accessibility Assistant using vision + conversation."""
    print("\n" + "="*70)
    print("👁️ DEMO: Accessibility Assistant (Vision + Conversation)")
    print("="*70)
    
    orchestrator = MultiAgentOrchestrator()
    orchestrator.register_agent("vision", VisionAnalystAgent())
    orchestrator.register_agent("conversation", ConversationAgent())
    
    print("\n📸 User captures their surroundings...")
    print("🎯 Question: What's in front of me?")
    
    tasks = [
        ("vision", "Describe the scene for a visually impaired person. Include: objects, people, potential obstacles, and navigation guidance."),
        ("conversation", "Based on the scene analysis, provide clear, conversational navigation guidance.")
    ]
    
    results = orchestrator.run_pipeline(tasks)


def main():
    """Run multi-agent demos."""
    print("=" * 70)
    print("🤖 HACKATHON MULTI-AGENT SYSTEM")
    print("Build Live Agent projects with specialized AI agents")
    print("=" * 70)
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY"):
        print("\n❌ Error: GEMINI_API_KEY not found in .env")
        return
    
    print("\n📚 These demos show how to build:")
    print("  • Homework Tutor - Vision + Planning + Conversation")
    print("  • Accessibility Assistant - Vision + Guidance")
    print("  • Any Live Agent project with specialized agents")
    
    print("\n" + "="*70)
    choice = input("\nRun demos? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("\n💡 TIP: Review the code to understand multi-agent patterns!")
        return
    
    # Run demos (will hit rate limit, but shows the pattern)
    try:
        demo_homework_tutor()
        print("\n\n" + "="*70)
        input("Press Enter to continue to next demo...")
        demo_accessibility_assistant()
    except Exception as e:
        print(f"\n⚠️ Demo stopped: {e}")
        print("\n💡 If you hit rate limits, the code structure shows:")
        print("  • How to create specialized agents")
        print("  • How to coordinate multiple agents")
        print("  • How to pass context between agents")
        print("  • Perfect foundation for your hackathon project!")


if __name__ == "__main__":
    main()
