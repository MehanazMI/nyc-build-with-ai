#!/usr/bin/env python3
"""
Level 3: Live Multimodal Agent
A real-time vision + conversation agent for the NYC AI Hackathon

Demonstrates:
- Real-time scene analysis
- Multi-turn contextual dialogue
- Vision + language understanding
- Natural conversation flow
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()


class LiveMultimodalAgent:
    """
    A live agent that sees, understands, and converses naturally.
    
    Perfect foundation for:
    - Vision-enabled tutors
    - Accessibility assistants
    - Real-time translators
    - Interactive guides
    """
    
    def __init__(self, api_key: str, agent_name: str = "Vision Assistant"):
        """
        Initialize the live agent.
        
        Args:
            api_key: Gemini API key
            agent_name: Name/personality for your agent
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'
        self.agent_name = agent_name
        
        # Conversation history for context
        self.chat_session = None
        self.current_image_uri = None
        self.conversation_history = []
        
        # Agent personality/instructions
        self.system_instruction = f"""You are {agent_name}, a helpful AI assistant with vision capabilities.

Your role:
- Analyze images and answer questions about what you see
- Provide clear, concise, and natural responses
- Maintain conversation context across multiple turns
- Be proactive in offering helpful insights
- Adapt your personality to be friendly and engaging

Guidelines:
- Keep responses focused and actionable (2-3 sentences typically)
- If you see something important, mention it proactively
- When asked "what do you see?", describe the scene naturally
- For follow-up questions, reference previous context
- Be honest if you're uncertain about something"""
    
    def upload_image(self, image_path: str) -> str:
        """
        Upload an image to use in conversation.
        
        Args:
            image_path: Path to image file
            
        Returns:
            File URI for use in prompts
        """
        print(f"\n👁️  Analyzing image: {os.path.basename(image_path)}")
        
        uploaded_file = self.client.files.upload(file=image_path)
        self.current_image_uri = uploaded_file.uri
        
        return uploaded_file.uri
    
    def start_conversation(self, image_path: str, initial_prompt: str = None):
        """
        Start a new conversation with an image.
        
        Args:
            image_path: Path to the image to analyze
            initial_prompt: Optional first question/prompt
        """
        # Upload the image
        file_uri = self.upload_image(image_path)
        
        # Create chat session
        self.chat_session = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.7
            )
        )
        
        # Initial analysis
        if initial_prompt is None:
            initial_prompt = "What do you see in this image? Give me a brief overview."
        
        print(f"\n💬 You: {initial_prompt}")
        print("⏳ Thinking...\n")
        
        # Send first message with image
        response = self.chat_session.send_message([
            types.Part.from_uri(file_uri=file_uri, mime_type='image/jpeg'),
            initial_prompt
        ])
        
        print(f"🤖 {self.agent_name}: {response.text}\n")
        
        # Store in history
        self.conversation_history.append({
            'user': initial_prompt,
            'agent': response.text,
            'has_image': True
        })
        
        return response.text
    
    def ask(self, question: str) -> str:
        """
        Continue the conversation with a follow-up question.
        
        Args:
            question: Your question or prompt
            
        Returns:
            Agent's response
        """
        if not self.chat_session:
            return "Error: No conversation started. Use start_conversation() first."
        
        print(f"\n💬 You: {question}")
        print("⏳ Thinking...\n")
        
        # Send follow-up message (image already in context)
        response = self.chat_session.send_message(question)
        
        print(f"🤖 {self.agent_name}: {response.text}\n")
        
        # Store in history
        self.conversation_history.append({
            'user': question,
            'agent': response.text,
            'has_image': False
        })
        
        return response.text
    
    def change_image(self, new_image_path: str, transition_prompt: str = None):
        """
        Switch to a new image while maintaining conversation context.
        
        Args:
            new_image_path: Path to new image
            transition_prompt: Optional prompt for the new image
        """
        if transition_prompt is None:
            transition_prompt = "I'm showing you a new image. What do you see now?"
        
        self.start_conversation(new_image_path, transition_prompt)
    
    def summarize_conversation(self) -> str:
        """Get a summary of the conversation so far."""
        if not self.conversation_history:
            return "No conversation yet."
        
        print("\n📝 Summarizing conversation...")
        
        summary_prompt = """Based on our conversation so far, provide a brief summary of:
        1. What we discussed
        2. Key points or insights
        3. Any conclusions or next steps
        
        Keep it concise (3-4 sentences)."""
        
        return self.ask(summary_prompt)


def interactive_demo(agent: LiveMultimodalAgent, image_path: str):
    """
    Run an interactive demo session.
    
    Args:
        agent: The multimodal agent
        image_path: Initial image to analyze
    """
    print("=" * 70)
    print(f"🚀 {agent.agent_name} - Interactive Mode")
    print("=" * 70)
    print("\nCommands:")
    print("  • Type your question and press Enter")
    print("  • 'new <path>' - Switch to a new image")
    print("  • 'summary' - Get conversation summary")
    print("  • 'quit' - Exit")
    print("\n" + "=" * 70)
    
    # Start with initial image
    agent.start_conversation(image_path)
    
    # Interactive loop
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thanks for chatting! See you at the hackathon!")
                break
            
            if user_input.lower() == 'summary':
                agent.summarize_conversation()
                continue
            
            if user_input.lower().startswith('new '):
                new_path = user_input[4:].strip()
                if os.path.exists(new_path):
                    agent.change_image(new_path)
                else:
                    print(f"❌ Image not found: {new_path}")
                continue
            
            # Regular question
            agent.ask(user_input)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("💡 Try rephrasing your question or check your API quota.")


def scripted_demo(agent: LiveMultimodalAgent, image_path: str):
    """
    Run a pre-scripted demo to showcase capabilities.
    
    Args:
        agent: The multimodal agent
        image_path: Image to analyze
    """
    print("=" * 70)
    print(f"🚀 {agent.agent_name} - Scripted Demo")
    print("=" * 70)
    print("\n🎬 Running automated demo to showcase capabilities...\n")
    
    # Demo conversation flow
    agent.start_conversation(
        image_path,
        "What do you see in this image? Be specific about objects and the scene."
    )
    
    input("Press Enter to continue...")
    
    agent.ask("What colors are most prominent in the image?")
    
    input("Press Enter to continue...")
    
    agent.ask("If this were a scene from a story, what might be happening?")
    
    input("Press Enter to continue...")
    
    agent.ask("What mood or atmosphere does this image convey?")
    
    input("Press Enter to continue...")
    
    print("\n" + "=" * 70)
    agent.summarize_conversation()
    print("=" * 70)


def main():
    """Main execution function."""
    
    parser = argparse.ArgumentParser(
        description="Level 3: Live Multimodal Agent Demo"
    )
    parser.add_argument(
        '--image',
        type=str,
        help='Path to image file (if not provided, uses sample)'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode (type your own questions)'
    )
    parser.add_argument(
        '--agent-name',
        type=str,
        default='Vision Assistant',
        help='Name for your agent (default: Vision Assistant)'
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        print("👉 Get your API key from: https://aistudio.google.com/")
        return
    
    # Determine image to use
    if args.image and os.path.exists(args.image):
        image_path = args.image
    else:
        # Use sample from vision-agent if available
        sample_dir = Path(__file__).parent.parent.parent / "examples" / "vision-agent" / "samples"
        if sample_dir.exists():
            sample_images = list(sample_dir.glob("*.jpg")) + list(sample_dir.glob("*.png"))
            if sample_images:
                image_path = str(sample_images[0])
            else:
                print("❌ No sample images found.")
                print("💡 Usage: python live_multimodal_agent.py --image path/to/image.jpg")
                return
        else:
            print("❌ No image provided and no samples found.")
            print("💡 Usage: python live_multimodal_agent.py --image path/to/image.jpg")
            return
    
    print(f"\n📸 Using image: {image_path}")
    
    # Initialize agent
    agent = LiveMultimodalAgent(api_key, agent_name=args.agent_name)
    
    # Run appropriate mode
    if args.interactive:
        interactive_demo(agent, image_path)
    else:
        scripted_demo(agent, image_path)
    
    # Final tips
    print("\n\n" + "=" * 70)
    print("🎉 Demo Complete!")
    print("=" * 70)
    print("\n💡 Next Steps for Your Hackathon Project:")
    print("\n1. 🎨 Customize the agent personality")
    print("   - Edit system_instruction in __init__")
    print("   - Make it domain-specific (tutor, guide, assistant)")
    print("\n2. 📸 Add webcam support")
    print("   - Use OpenCV to capture live frames")
    print("   - Process frames in real-time")
    print("\n3. 🎤 Add voice input/output")
    print("   - Integrate speech-to-text for questions")
    print("   - Add text-to-speech for responses")
    print("\n4. 🔧 Add specialized tools")
    print("   - OCR for text extraction")
    print("   - Object detection for counting")
    print("   - Translation for multilingual support")
    print("\n5. 🚀 Polish the UX")
    print("   - Create a web interface")
    print("   - Add visual feedback")
    print("   - Handle errors gracefully")
    print("\n" + "=" * 70)
    print("\n📚 Resources:")
    print("  • Gemini Live API: https://ai.google.dev/gemini-api/docs/live-api")
    print("  • ADK Guide: https://cloud.google.com/vertex-ai/docs/agent-builder")
    print("  • Hackathon Slack: https://gdg-nyc.slack.com")
    print("\n🏆 Good luck at the hackathon! Build something amazing!")


if __name__ == "__main__":
    main()
