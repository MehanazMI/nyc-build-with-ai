#!/usr/bin/env python3
"""
Voice Agent - Real-time Audio Conversation with Gemini Live API
Demonstrates voice-enabled AI interaction with low latency.
"""

import os
import asyncio
import pyaudio
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


class VoiceAgent:
    """Voice-enabled AI agent using Gemini Live API."""
    
    def __init__(self, api_key: str):
        """Initialize the voice agent.
        
        Args:
            api_key: Google Gemini API key
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash-exp"
        self.audio = pyaudio.PyAudio()
        self.is_listening = False
        
    async def start_conversation(self):
        """Start a voice conversation with the agent."""
        
        system_instruction = """You are a friendly and helpful voice assistant.
        
        Guidelines:
        - Keep responses concise (2-3 sentences for most queries)
        - Speak naturally and conversationally
        - Ask clarifying questions when needed
        - Be engaging and show personality
        - If you hear background noise or unclear audio, politely ask user to repeat
        
        You're designed for voice interaction, so avoid:
        - Long lists or detailed technical explanations
        - Suggesting "click here" or "see link" (use voice-appropriate alternatives)
        - Complex formatting or tables"""
        
        print("🎤 Voice Agent Ready!")
        print("=" * 70)
        print("\n🎯 Features:")
        print("  • Real-time speech-to-speech")
        print("  • Natural conversation flow")
        print("  • Interrupt anytime to ask new questions")
        print("\n💬 Try saying:")
        print("  • 'Tell me about the NYC AI Hackathon'")
        print("  • 'What is Gemini Live API?'")
        print("  • 'Help me brainstorm a hackathon project'")
        print("\n⚠️  Note: This is a simplified demo. Full implementation requires:")
        print("  • WebRTC or similar for streaming audio")
        print("  • VAD (Voice Activity Detection)")
        print("  • Audio preprocessing")
        print("\n" + "=" * 70)
        
        # For demo purposes, we'll simulate text-based interaction
        # Real implementation would stream audio
        print("\n🔧 DEMO MODE: Using text input (microphone streaming requires additional setup)")
        print("Type your questions (or 'quit' to exit):\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thanks for chatting! Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Generate response
            print("\n🤖 Agent: ", end="", flush=True)
            
            async for chunk in self._generate_streaming_response(user_input, system_instruction):
                print(chunk, end="", flush=True)
            
            print("\n")
    
    async def _generate_streaming_response(self, prompt: str, system_instruction: str):
        """Generate streaming response.
        
        Args:
            prompt: User's input
            system_instruction: System instructions
            
        Yields:
            Response chunks
        """
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "system_instruction": system_instruction,
                "temperature": 0.7
            }
        )
        
        # Simulate streaming by yielding the response
        # In real implementation, this would be actual streaming chunks
        yield response.text
    
    def cleanup(self):
        """Clean up audio resources."""
        self.audio.terminate()


class VoiceAgentFullExample:
    """
    Full voice agent implementation with audio streaming.
    
    NOTE: This requires additional setup:
    1. Audio input/output device configuration
    2. Voice Activity Detection (VAD)
    3. Audio preprocessing (noise reduction, echo cancellation)
    4. Proper async audio streaming
    """
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.audio = pyaudio.PyAudio()
        
    def list_audio_devices(self):
        """List available audio devices."""
        print("\n🎤 Available Audio Devices:")
        print("-" * 70)
        
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            print(f"{i}: {info['name']}")
            print(f"   Input Channels: {info['maxInputChannels']}")
            print(f"   Output Channels: {info['maxOutputChannels']}")
            print()
    
    async def stream_audio_conversation(self):
        """
        Stream audio for real-time conversation.
        
        This is a skeleton for full implementation.
        Production-ready version needs:
        - VAD to detect when user is speaking
        - Audio chunking and buffering
        - Interrupt handling
        - Error recovery
        """
        print("🎤 Full streaming audio conversation")
        print("⚠️  Implementation requires production-grade audio handling")
        print("📚 See Gemini Live API docs for complete examples")


async def main():
    """Main execution function."""
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        print("👉 Get your API key from: https://aistudio.google.com/")
        return
    
    print("🚀 Voice Agent - Gemini Live API Demo")
    print("=" * 70)
    print()
    
    # Check PyAudio installation
    try:
        import pyaudio
        audio = pyaudio.PyAudio()
        audio.terminate()
        print("✅ PyAudio detected - audio capabilities available")
    except ImportError:
        print("⚠️  PyAudio not installed - limited functionality")
        print("   Install with: pip install pyaudio")
        print("   Windows users: pip install pipwin && pipwin install pyaudio")
    
    # Initialize and run voice agent
    agent = VoiceAgent(api_key)
    
    try:
        await agent.start_conversation()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        agent.cleanup()
        print("\n✅ Agent shut down successfully")
    
    print("\n" + "=" * 70)
    print("🎓 Next Steps for Your Hackathon Project:")
    print("=" * 70)
    print("\n1. 🎤 Add real audio streaming")
    print("   - Use WebRTC or similar for low-latency audio")
    print("   - Implement VAD (Voice Activity Detection)")
    print("\n2. 🎯 Specialize your agent")
    print("   - Real-time translator")
    print("   - Interactive tutor")
    print("   - Accessibility assistant")
    print("\n3. 🎨 Enhance UX")
    print("   - Visual feedback during listening/thinking")
    print("   - Allow interruptions mid-response")
    print("   - Add voice effects or modulation")
    print("\n4. 📱 Deploy")
    print("   - Mobile app integration")
    print("   - Web interface with WebRTC")
    print("   - Edge device deployment")


if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("  • Check your GEMINI_API_KEY is set correctly")
        print("  • Ensure you have microphone permissions")
        print("  • Verify PyAudio is installed properly")
