#!/usr/bin/env python3
"""
Level 0: Space Explorer Avatar Generator
Way Back Home - Official Workshop Pattern (with Auto-Fallback)

Demonstrates:
- Multi-turn IMAGE generation with Gemini (Nano Banana 🍌)
- Character consistency across multiple images
- Chat sessions for maintaining visual context
- Automatic fallback to text descriptions if image generation unavailable
"""

import os
import io
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()


class AvatarGenerator:
    """
    Generate consistent character avatars using multi-turn generation.
    
    Key Learning: Using a CHAT SESSION (not independent calls) maintains
    consistency across multiple generations.
    
    Automatically detects available models and falls back gracefully.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the generator with automatic model detection.
        
        Args:
            api_key: Gemini API key
        """
        self.client = genai.Client(api_key=api_key)
        self.supports_image_generation = False
        self.model_name = None
        
        # Try image generation models in order of preference
        image_models = [
            'gemini-2.0-flash-exp',
            'gemini-2.5-flash-image',
            'gemini-2.0-flash-image'
        ]
        
        # Try text models as fallback
        text_models = [
            'gemini-2.5-flash',
            'gemini-2.0-flash-001',
            'gemini-1.5-flash'
        ]
        
        print("🔍 Detecting available models...")
        
        # First, try to find image generation model
        for model in image_models:
            try:
                # Quick test with actual message to verify it works
                test_chat = self.client.chats.create(
                    model=model,
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"]
                    )
                )
                # Try to actually send a message
                test_response = test_chat.send_message("test")
                self.model_name = model
                self.supports_image_generation = True
                print(f"✅ Found image generation model: {model}")
                break
            except Exception as e:
                # Model doesn't support image generation
                continue
        
        # If no image model found, use text model
        if not self.model_name:
            print("⚠️  Image generation not available (requires Vertex AI)")
            print("📝 Falling back to detailed text descriptions...")
            
            for model in text_models:
                try:
                    # Test if model is available
                    self.client.models.generate_content(
                        model=model,
                        contents="test"
                    )
                    self.model_name = model
                    print(f"✅ Using text model: {model}")
                    break
                except Exception:
                    continue
        
        if not self.model_name:
            raise Exception("❌ No compatible models available. Check your API key.")
    
    def generate_explorer_avatar(
        self, 
        username: str,
        appearance: str,
        suit_color: str,
        output_dir: str = "outputs"
    ) -> Dict[str, str]:
        """
        Generate portrait and icon using multi-turn chat for consistency.
        
        The key technique: Using a CHAT SESSION rather than independent API calls.
        This allows Gemini to "remember" what it created in the first turn,
        ensuring the icon matches the portrait.
        
        Args:
            username: Explorer name
            appearance: Physical appearance description
            suit_color: Space suit color
            output_dir: Directory to save outputs
            
        Returns:
            Dict with portrait_path, icon_path, and mode
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n🚀 Generating avatar for {username}...")
        print(f"   Appearance: {appearance}")
        print(f"   Suit: {suit_color}")
        print(f"   Mode: {'🎨 IMAGE GENERATION' if self.supports_image_generation else '📝 TEXT DESCRIPTION'}\n")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 1: Create Chat Session for Multi-Turn Generation
        # ═══════════════════════════════════════════════════════════════
        
        if self.supports_image_generation:
            chat = self.client.chats.create(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    temperature=0.8
                )
            )
        else:
            # Text-only mode for learning the pattern
            chat = self.client.chats.create(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    temperature=0.8
                )
            )
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 2: Generate the Portrait (First Turn)
        # ═══════════════════════════════════════════════════════════════
        
        portrait_prompt = f"""Create a stylized space explorer portrait.

Character appearance: {appearance}
Name on suit patch: "{username}"
Suit color: {suit_color}

CRITICAL STYLE REQUIREMENTS:
- Digital illustration style, clean lines, vibrant saturated colors
- Futuristic but weathered space suit with visible mission patches
- Background: Pure solid white (#FFFFFF) - absolutely no gradients, patterns, or elements
- Frame: Head and shoulders only, 3/4 view facing slightly left
- Lighting: Soft diffused studio lighting, no harsh shadows
- Expression: Determined but approachable
- Art style: Modern animated movie character portrait (similar to Pixar or Dreamworks style)

The white background is essential - the avatar will be composited onto a map."""
        
        print("🎨 Generating portrait...")
        portrait_response = chat.send_message(portrait_prompt)
        
        # Extract the image or text description
        portrait_image = None
        portrait_description = ""
        
        if self.supports_image_generation:
            for part in portrait_response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_bytes = part.inline_data.data
                    portrait_image = Image.open(io.BytesIO(image_bytes))
                    
                    portrait_path = os.path.join(output_dir, f"{username}_portrait.png")
                    portrait_image.save(portrait_path)
                    print(f"✓ Portrait generated: {portrait_path}")
                    break
            
            if portrait_image is None:
                raise Exception("Failed to generate portrait - no image in response")
        else:
            # Text mode: Save detailed description
            portrait_description = portrait_response.text if hasattr(portrait_response, 'text') else str(portrait_response)
            portrait_path = os.path.join(output_dir, f"{username}_portrait.txt")
            with open(portrait_path, 'w', encoding='utf-8') as f:
                f.write(f"PORTRAIT DESCRIPTION\n")
                f.write(f"{'='*60}\n\n")
                f.write(portrait_description if portrait_description else "No description generated")
            print(f"✓ Portrait description saved: {portrait_path}")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 3: Generate the Icon (Second Turn - SAME CHAT!)
        # ═══════════════════════════════════════════════════════════════
        
        icon_prompt = """Now create a circular map icon of this SAME character.

CRITICAL REQUIREMENTS:
- SAME person, SAME face, SAME expression, SAME suit — maintain perfect consistency with the portrait
- Tighter crop: just the head and very top of shoulders
- Background: Pure solid white (#FFFFFF)
- Optimized for small display sizes (will be used as a 64px map marker)
- Keep the exact same art style, colors, and lighting as the portrait
- Square 1:1 aspect ratio

This icon must be immediately recognizable as the same character from the portrait."""
        
        print("🖼️  Creating map icon...")
        icon_response = chat.send_message(icon_prompt)
        
        # Extract the icon image or text description
        icon_image = None
        
        if self.supports_image_generation:
            for part in icon_response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_bytes = part.inline_data.data
                    icon_image = Image.open(io.BytesIO(image_bytes))
                    
                    icon_path = os.path.join(output_dir, f"{username}_icon.png")
                    icon_image.save(icon_path)
                    print(f"✓ Icon generated: {icon_path}")
                    break
            
            if icon_image is None:
                raise Exception("Failed to generate icon - no image in response")
        else:
            # Text mode: Save icon description
            icon_description = icon_response.text if hasattr(icon_response, 'text') else str(icon_response)
            icon_path = os.path.join(output_dir, f"{username}_icon.txt")
            with open(icon_path, 'w', encoding='utf-8') as f:
                f.write(f"ICON DESCRIPTION\n")
                f.write(f"{'='*60}\n\n")
                f.write(icon_description if icon_description else "No description generated")
            print(f"✓ Icon description saved: {icon_path}")
        
        return {
            "portrait_path": portrait_path,
            "icon_path": icon_path,
            "mode": "image" if self.supports_image_generation else "text"
        }


def demo_avatar_generation():
    """Run a demo of avatar generation."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        print("👉 Get your API key from: https://aistudio.google.com/")
        return
    
    generator = AvatarGenerator(api_key)
    
    print("═" * 70)
    print("  🎨 LEVEL 0: SPACE EXPLORER AVATAR GENERATOR")
    print("  Multi-Turn Chat for Consistency (Nano Banana 🍌)")
    print("═" * 70)
    
    # Example 1: Commander
    print("\n\n📸 Example 1: Commander Sarah Chen")
    print("─" * 70)
    
    result1 = generator.generate_explorer_avatar(
        username="Commander_Chen",
        appearance="East Asian woman, short black hair, confident gaze, small scar above left eyebrow",
        suit_color="Navy blue with gold trim"
    )
    
    print(f"\n✅ Complete!")
    print(f"   Portrait: {result1['portrait_path']}")
    print(f"   Icon: {result1['icon_path']}")
    
    if result1['mode'] == 'text':
        print(f"\n📖 Open the .txt files to see detailed character descriptions!")
    
    input("\n\nPress Enter for next example...")
    
    # Example 2: Engineer
    print("\n\n📸 Example 2: Engineer Marcus Rodriguez")
    print("─" * 70)
    
    result2 = generator.generate_explorer_avatar(
        username="Eng_Rodriguez",
        appearance="Hispanic man, curly brown hair, warm smile, wearing smart glasses",
        suit_color="Orange with reflective stripes"
    )
    
    print(f"\n✅ Complete!")
    print(f"   Portrait: {result2['portrait_path']}")
    print(f"   Icon: {result2['icon_path']}")
    
    print("\n\n" + "═" * 70)
    print("  🎉 DEMO COMPLETE!")
    print("═" * 70)
    
    if generator.supports_image_generation:
        print("\n🎨 You have IMAGE GENERATION enabled!")
        print("📸 Check your outputs/ folder for PNG images!")
    else:
        print("\n📝 Running in TEXT MODE (Image generation requires Vertex AI)")
        print("📖 Check your outputs/ folder for detailed descriptions!")
        print("\n💡 At the hackathon (March 7-8), you'll have full image generation!")
    
    print("\n📚 Key Concepts Demonstrated:")
    print("\n1. 🔗 **Multi-Turn Chat Sessions**")
    print("   - client.chats.create() maintains context")
    print("   - Second turn remembers the first")
    print("   - Result: Consistent character across generations\n")
    
    print("2. 🎨 **Image Generation with Gemini**")
    print("   - Model: gemini-2.0-flash-exp (requires Vertex AI access)")
    print("   - response_modalities=['TEXT', 'IMAGE']")
    print("   - Workshop runs in Google Cloud Shell with special permissions\n")
    
    print("3. 📝 **Prompt Engineering**")
    print("   - Subject definition (space explorer portrait)")
    print("   - Style requirements (Pixar/Dreamworks)")
    print("   - Technical constraints (white background)")
    print("   - Variable injection (username, appearance, color)\n")
    
    print("4. 🔄 **Consistency Through Context**")
    print("   - First turn establishes character")
    print("   - Second turn references 'SAME character'")
    print("   - Chat context = consistency\n")
    
    print("5. 🛠️ **Automatic Fallback**")
    print("   - Detects available models automatically")
    print("   - Falls back to text if image generation unavailable")
    print("   - Same pattern works for both modes\n")
    
    print("═" * 70)
    print("\n💡 Why This Matters for Hackathon:")
    print("\n**Without chat session:**")
    print("  Call 1: Person A")
    print("  Call 2: Person B  ❌ Different!")
    
    print("\n**With chat session:**")
    print("  Turn 1: Person A")
    print("  Turn 2: Person A  ✅ Same!")
    
    print("\n🏆 Hackathon Applications:")
    print("  • Character design tools")
    print("  • Consistent avatar generation")
    print("  • Multi-angle product visualization")
    print("  • Story illustration (same characters)")
    print("  • Game asset generation\n")
    
    print("═" * 70)
    print("\n📸 Check your outputs/ folder to see the results!")
    
    if generator.supports_image_generation:
        print("🍌 Powered by Nano Banana (Gemini Image Generation)")
    else:
        print("📝 Text descriptions demonstrate the multi-turn pattern")
        print("🍌 Full image generation available at hackathon (Vertex AI)")


if __name__ == "__main__":
    demo_avatar_generation()
