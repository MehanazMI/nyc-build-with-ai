#!/usr/bin/env python3
"""
Level 1: Multi-Agent Systems - "Way Back Home"
Implement a coordinated multi-agent system with specialized roles
"""

import os
from typing import List, Dict
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()


class Agent:
    """Base agent class with specialized capabilities."""
    
    def __init__(self, client: genai.Client, role: str, system_instruction: str):
        """Initialize an agent.
        
        Args:
            client: Gemini client
            role: Agent's role/name
            system_instruction: Instructions defining agent behavior
        """
        self.client = client
        self.role = role
        self.system_instruction = system_instruction
        self.model_name = 'gemini-2.5-flash'
        
    def process(self, task: str, context: str = "") -> str:
        """Process a task.
        
        Args:
            task: The task to perform
            context: Additional context from previous agents
            
        Returns:
            Agent's response
        """
        full_prompt = f"{context}\n\nTask: {task}" if context else task
        
        print(f"\n🤖 {self.role} is thinking...")
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.7
            )
        )
        
        return response.text


class PlannerAgent(Agent):
    """Agent specialized in strategic planning."""
    
    def __init__(self, client: genai.Client):
        system_instruction = """You are a Strategic Planner Agent.
        
        Your role:
        - Break down complex problems into actionable steps
        - Create high-level strategies and roadmaps
        - Identify key milestones and dependencies
        - Think systematically about goals and constraints
        
        Provide clear, structured plans with:
        1. Goal statement
        2. Key steps (numbered)
        3. Success criteria
        4. Potential challenges
        
        Be concise but thorough."""
        
        super().__init__(client, "Strategic Planner", system_instruction)


class ResearchAgent(Agent):
    """Agent specialized in information gathering and analysis."""
    
    def __init__(self, client: genai.Client):
        system_instruction = """You are a Research Analyst Agent.
        
        Your role:
        - Analyze information systematically
        - Identify key facts, patterns, and insights
        - Consider multiple perspectives
        - Provide evidence-based recommendations
        
        Structure your analysis:
        1. Key Findings
        2. Analysis & Insights
        3. Recommendations
        
        Be objective and thorough."""
        
        super().__init__(client, "Research Analyst", system_instruction)


class WriterAgent(Agent):
    """Agent specialized in content creation."""
    
    def __init__(self, client: genai.Client):
        system_instruction = """You are a Creative Writer Agent.
        
        Your role:
        - Transform ideas and plans into compelling narratives
        - Write clearly, engagingly, and persuasively
        - Adapt tone and style to the audience
        - Weave together different elements into cohesive content
        
        Create content that:
        - Captures attention
        - Communicates clearly
        - Maintains flow and structure
        - Includes specific details and examples
        
        Be creative but stay on message."""
        
        super().__init__(client, "Creative Writer", system_instruction)


class CoordinatorAgent(Agent):
    """Agent that coordinates other agents."""
    
    def __init__(self, client: genai.Client):
        system_instruction = """You are a Coordinator Agent.
        
        Your role:
        - Understand the overall goal
        - Determine which agents to involve
        - Synthesize agent outputs
        - Ensure coherent final result
        
        Think about:
        - What information is needed from each agent?
        - How should results be combined?
        - Is the final output complete and coherent?"""
        
        super().__init__(client, "Coordinator", system_instruction)


class MultiAgentSystem:
    """Orchestrate multiple agents working together."""
    
    def __init__(self, api_key: str):
        """Initialize the multi-agent system.
        
        Args:
            api_key: Google Gemini API key
        """
        self.client = genai.Client(api_key=api_key)
        
        # Initialize specialized agents
        self.planner = PlannerAgent(self.client)
        self.researcher = ResearchAgent(self.client)
        self.writer = WriterAgent(self.client)
        self.coordinator = CoordinatorAgent(self.client)
        
    def solve_problem(self, problem: str) -> Dict[str, str]:
        """Solve a problem using coordinated agents.
        
        Args:
            problem: The problem to solve
            
        Returns:
            Dictionary with results from each agent
        """
        print("=" * 70)
        print(f"🎯 PROBLEM: {problem}")
        print("=" * 70)
        
        results = {}
        
        # Step 1: Planner creates strategy
        print("\n📋 Phase 1: Strategic Planning")
        plan = self.planner.process(
            f"Create a strategic plan to address: {problem}"
        )
        results['plan'] = plan
        print(f"\n✅ Plan created:\n{plan[:200]}...")
        
        # Step 2: Researcher analyzes
        print("\n🔍 Phase 2: Research & Analysis")
        research = self.researcher.process(
            f"Analyze this problem and plan. Provide insights and recommendations: {problem}",
            context=f"Strategic Plan:\n{plan}"
        )
        results['research'] = research
        print(f"\n✅ Research completed:\n{research[:200]}...")
        
        # Step 3: Writer creates final content
        print("\n✍️  Phase 3: Content Creation")
        final_content = self.writer.process(
            f"Create a comprehensive solution document for: {problem}",
            context=f"Plan:\n{plan}\n\nResearch:\n{research}"
        )
        results['content'] = final_content
        print(f"\n✅ Content created")
        
        # Step 4: Coordinator synthesizes
        print("\n🔄 Phase 4: Coordination & Synthesis")
        synthesis = self.coordinator.process(
            "Provide an executive summary of the solution",
            context=f"Problem: {problem}\n\nPlan:\n{plan}\n\nResearch:\n{research}\n\nSolution:\n{final_content}"
        )
        results['synthesis'] = synthesis
        
        return results
    
    def print_results(self, results: Dict[str, str]):
        """Pretty print the results.
        
        Args:
            results: Dictionary of agent results
        """
        print("\n\n" + "=" * 70)
        print("📊 MULTI-AGENT SYSTEM RESULTS")
        print("=" * 70)
        
        print("\n📋 STRATEGIC PLAN")
        print("-" * 70)
        print(results['plan'])
        
        print("\n\n🔍 RESEARCH & ANALYSIS")
        print("-" * 70)
        print(results['research'])
        
        print("\n\n✍️  FINAL SOLUTION")
        print("-" * 70)
        print(results['content'])
        
        print("\n\n🎯 EXECUTIVE SUMMARY")
        print("-" * 70)
        print(results['synthesis'])
        print("\n" + "=" * 70)


def main():
    """Main execution function."""
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        print("👉 Get your API key from: https://aistudio.google.com/")
        return
    
    print("🚀 Level 1: Multi-Agent Systems - Way Back Home")
    print("=" * 70)
    print()
    
    # Initialize multi-agent system
    system = MultiAgentSystem(api_key)
    
    # Example problem
    problem = """Design an AI-powered mobile app that helps people reduce their carbon footprint 
    through daily habit tracking and personalized recommendations. The app should be engaging, 
    educational, and use gamification to encourage sustainable behaviors."""
    
    # Solve the problem using multiple agents
    results = system.solve_problem(problem)
    
    # Display results
    system.print_results(results)
    
    print("\n\n🎉 Level 1 Complete!")
    print("=" * 70)
    print("\n📚 What You Learned:")
    print("  ✓ Agent specialization and roles")
    print("  ✓ Sequential agent orchestration")
    print("  ✓ Context sharing between agents")
    print("  ✓ Result synthesis and coordination")
    print("\n🚀 Next Steps:")
    print("  • Experiment with different agent combinations")
    print("  • Try parallel agent execution")
    print("  • Build your hackathon project!")
    print("\n💡 Ideas for Your Hackathon Project:")
    print("  • Live Agent: Real-time voice/vision assistant")
    print("  • Creative Storyteller: Multi-modal content generator")


if __name__ == "__main__":
    main()
