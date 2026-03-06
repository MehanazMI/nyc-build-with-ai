#!/usr/bin/env python3
"""
Quick Setup Test Script
Run this to verify your environment is ready for the hackathon!
"""

import sys
import os

def check_imports():
    """Check if required packages are installed."""
    checks = {
        "✅ Python": sys.version.split()[0],
        "❓ python-dotenv": False,
        "❓ google-genai": False,
        "❓ Pillow (PIL)": False,
    }
    
    try:
        import dotenv
        checks["❓ python-dotenv"] = "✅ Installed"
    except ImportError:
        checks["❓ python-dotenv"] = "❌ Missing - Run: pip install python-dotenv"
    
    try:
        from google import genai
        checks["❓ google-genai"] = "✅ Installed"
    except ImportError:
        checks["❓ google-genai"] = "❌ Missing - Run: pip install google-genai"
    
    try:
        from PIL import Image
        checks["❓ Pillow (PIL)"] = "✅ Installed"
    except ImportError:
        checks["❓ Pillow (PIL)"] = "❌ Missing - Run: pip install Pillow"
    
    return checks

def check_env():
    """Check environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key and api_key != "your-gemini-api-key-here":
        return "✅ API key configured"
    elif api_key == "your-gemini-api-key-here":
        return "⚠️ Please update .env with your actual API key"
    else:
        return "❌ API key not found in .env"

def main():
    print("=" * 60)
    print("🚀 NYC AI HACKATHON 2026 - SETUP CHECK")
    print("=" * 60)
    print()
    
    print("📦 Checking Python packages...")
    print("-" * 60)
    checks = check_imports()
    for name, status in checks.items():
        print(f"{name}: {status}")
    
    print()
    print("🔑 Checking API configuration...")
    print("-" * 60)
    env_status = check_env()
    print(f"Gemini API Key: {env_status}")
    
    print()
    print("=" * 60)
    
    all_installed = all("✅" in str(v) for v in checks.values())
    api_ready = "✅" in env_status
    
    if all_installed and api_ready:
        print("🎉 SUCCESS! You're ready for the hackathon!")
        print()
        print("Next steps:")
        print("  1. Review Level 3 examples:")
        print("     cd codelabs\\level-3")
        print("     python live_multimodal_agent.py")
        print()
        print("  2. Choose your track:")
        print("     • Live Agent: Real-time voice + vision")
        print("     • Creative Storyteller: Rich narratives")
        print()
        print("  3. Pick a project idea from:")
        print("     codelabs/level-3/HACKATHON-IDEAS.md")
    elif all_installed and not api_ready:
        print("⚠️ ALMOST THERE!")
        print()
        print("Add your Gemini API key:")
        print("  1. Visit: https://aistudio.google.com/")
        print("  2. Get your API key")
        print("  3. Edit .env file and add: GEMINI_API_KEY=your-key-here")
        print("  4. Run this script again")
    else:
        print("❌ Setup incomplete - Install missing packages:")
        print()
        print("Run: pip install -r requirements.txt")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
