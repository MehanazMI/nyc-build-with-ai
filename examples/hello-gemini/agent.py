#!/usr/bin/env python3
"""
Hello Gemini - Your First Multimodal Agent
A simple example to test Gemini API connectivity.
"""

import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

def main():
    """Initialize and test Gemini API."""
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        print("👉 Get your API key from: https://aistudio.google.com/")
        return
    
    # Create Gemini client
    client = genai.Client(api_key=api_key)
    
    print("🚀 Testing Gemini API Connection...\n")
    
    # Test prompt
    prompt = """You are an AI agent for the NYC Build With AI Hackathon 2026. 
    Introduce yourself in a creative and enthusiastic way. 
    Mention that you're excited to help build multimodal AI experiences."""
    
    print("💬 Sending prompt to Gemini...\n")
    
    # Generate response
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    print("✅ Response from Gemini:\n")
    print("-" * 60)
    print(response.text)
    print("-" * 60)
    print("\n🎉 Success! Your Gemini API is working!")
    print("\n📚 Next steps:")
    print("  1. Try modifying the prompt above")
    print("  2. Explore voice capabilities in examples/voice-agent/")
    print("  3. Test vision features in examples/vision-agent/")
    print("  4. Start Level 0 codelab: https://codelabs.developers.google.com/way-back-home-level-0/")

if __name__ == "__main__":
    main()
