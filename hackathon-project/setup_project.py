#!/usr/bin/env python3
"""
Hackathon Project Setup
Initialize your project structure and configuration.
"""

import os
from pathlib import Path


def create_directory_structure():
    """Create the project directory structure."""
    
    directories = [
        "src",
        "src/utils",
        "src/agents",
        "src/models",
        "tests",
        "docs",
        "data",
        "assets"
    ]
    
    print("📁 Creating project directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}/")
    
    print("\n✅ Directory structure created!")


def create_source_files():
    """Create starter source files."""
    
    files = {
        "src/main.py": '''#!/usr/bin/env python3
"""
Main entry point for your hackathon project.
"""

import os
from dotenv import load_dotenv
from agent import MyAgent

# Load environment variables
load_dotenv()


def main():
    """Run your agent."""
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found")
        return
    
    print("🚀 Starting your hackathon project...")
    print("=" * 70)
    
    # Initialize your agent
    agent = MyAgent(api_key)
    
    # Run your agent
    agent.run()
    
    print("\\n✅ Done!")


if __name__ == "__main__":
    main()
''',
        
        "src/agent.py": '''#!/usr/bin/env python3
"""
Your AI agent implementation.
"""

from google import genai
from google.genai import types


class MyAgent:
    """Your custom AI agent."""
    
    def __init__(self, api_key: str):
        """Initialize the agent.
        
        Args:
            api_key: Gemini API key
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash-exp"
        
    def run(self):
        """Run the agent."""
        
        print("🤖 Agent initialized!")
        print("\\n💡 TODO: Implement your agent logic here")
        
        # Example: Simple interaction
        response = self.client.models.generate_content(
            model=self.model_name,
            contents="Hello! I'm ready to build something amazing."
        )
        
        print(f"\\n✨ Agent says: {response.text}")
''',
        
        "src/config.py": '''#!/usr/bin/env python3
"""
Configuration settings for your project.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash-exp"

# Agent Configuration
AGENT_NAME = "MyAgent"
AGENT_DESCRIPTION = "An AI agent for the NYC AI Hackathon"

# System Instructions
SYSTEM_INSTRUCTION = """You are an AI agent built for the NYC AI Hackathon.
Your goal is to help users with [specific task].

Be helpful, creative, and engaging."""

# Model Parameters
TEMPERATURE = 0.7
MAX_TOKENS = 2048

# Feature Flags
ENABLE_VOICE = False
ENABLE_VISION = False
ENABLE_MULTIMODAL = True
''',
        
        "src/utils/__init__.py": "# Utility functions\n",
        
        "tests/test_agent.py": '''#!/usr/bin/env python3
"""
Tests for your agent.
"""

import unittest
from src.agent import MyAgent


class TestMyAgent(unittest.TestCase):
    """Test cases for MyAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        # TODO: Add test setup
        pass
    
    def test_initialization(self):
        """Test agent initialization."""
        # TODO: Add test
        pass
    
    def test_agent_response(self):
        """Test agent responses."""
        # TODO: Add test
        pass


if __name__ == "__main__":
    unittest.main()
''',
        
        "docs/DEMO-GUIDE.md": '''# Demo Guide

## 🎯 Your Demo Presentation

**Duration:** 3-5 minutes

### Structure

1. **Problem** (30 seconds)
   - What problem are you solving?
   - Why does it matter?

2. **Solution** (30 seconds)
   - What did you build?
   - How does it work?

3. **Live Demo** (2-3 minutes)
   - Show the key features
   - Interactive demonstration
   - Highlight multimodal capabilities

4. **Technical Highlights** (30-60 seconds)
   - Key technologies used
   - Interesting technical challenges solved

5. **Future Vision** (30 seconds)
   - What's next?
   - Potential impact

### Demo Tips

✅ **Do:**
- Start with a compelling hook
- Show, don't just tell
- Make it interactive
- Have a backup plan
- Practice your timing
- Highlight multimodal features

❌ **Don't:**
- Apologize for missing features
- Spend too much time on setup
- Show too many features
- Go over time
- Read slides

### Technical Checklist

Before your demo:
- [ ] Test on presentation laptop
- [ ] Check internet connection
- [ ] Prepare sample inputs
- [ ] Have screenshots as backup
- [ ] Close unnecessary apps
- [ ] Disable notifications

### Backup Plan

If technical issues occur:
1. Have a pre-recorded demo video ready
2. Prepare screenshots of key features
3. Be ready to explain conceptually

### Questions to Prepare For

- How does this use Gemini's multimodal capabilities?
- What was the biggest technical challenge?
- How would you scale this?
- What's the user value?
- How is this different from existing solutions?

---

Good luck! 🚀
''',
        
        "data/.gitkeep": "",
        "assets/.gitkeep": ""
    }
    
    print("\n📝 Creating source files...")
    for filepath, content in files.items():
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ {filepath}")
    
    print("\n✅ Source files created!")


def print_next_steps():
    """Print next steps for the user."""
    
    print("\n" + "=" * 70)
    print("🎉 PROJECT SETUP COMPLETE!")
    print("=" * 70)
    
    print("\n📋 Next Steps:")
    print("\n1. Define your project:")
    print("   • Edit PROJECT-PLAN.md with your idea")
    print("   • Choose your track (Live Agent or Creative Storyteller)")
    
    print("\n2. Implement your agent:")
    print("   • Edit src/agent.py with your logic")
    print("   • Configure src/config.py")
    print("   • Add utilities to src/utils/")
    
    print("\n3. Test your code:")
    print("   • Run: python src/main.py")
    print("   • Test: python -m pytest tests/")
    
    print("\n4. Prepare demo:")
    print("   • Follow docs/DEMO-GUIDE.md")
    print("   • Practice your presentation")
    
    print("\n📚 Helpful Resources:")
    print("   • Examples: ../examples/")
    print("   • Codelabs: ../codelabs/")
    print("   • Documentation: ../README.md")
    
    print("\n🚀 Start building!")
    print("=" * 70)


def main():
    """Main setup function."""
    
    print("🚀 NYC AI Hackathon - Project Setup")
    print("=" * 70)
    print()
    
    # Create directories
    create_directory_structure()
    
    # Create files
    create_source_files()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
