#!/usr/bin/env python3
"""
Level 0: Identity Generation - "Way Back Home"
Generate consistent character identities using Gemini
"""

import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()


class IdentityGenerator:
    """Generate and manage character identities."""
    
    def __init__(self, api_key: str):
        """Initialize the identity generator.
        
        Args:
            api_key: Google Gemini API key
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'
        
    def generate_identity(self, theme: str = "fantasy adventure") -> dict:
        """Generate a character identity.
        
        Args:
            theme: The theme/genre for the character
            
        Returns:
            Dictionary containing character details
        """
        system_instruction = """You are an expert character designer and storyteller.
        Generate rich, detailed character identities that are:
        - Unique and memorable
        - Internally consistent
        - Emotionally compelling
        - Suitable for storytelling
        
        Always respond with valid JSON following this exact structure:
        {
            "name": "character name",
            "age": number,
            "background": "2-3 sentence backstory",
            "personality": ["trait1", "trait2", "trait3"],
            "motivation": "primary goal or desire",
            "skills": ["skill1", "skill2", "skill3"],
            "weakness": "character flaw or vulnerability",
            "appearance": "brief physical description"
        }"""
        
        prompt = f"Create a unique character for a {theme} story."
        
        print(f"🎭 Generating character identity for theme: {theme}")
        print("⏳ Thinking...\n")
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.8,  # Higher for creativity
                response_mime_type="application/json"
            )
        )
        
        # Parse JSON response
        character_data = json.loads(response.text)
        return character_data
    
    def print_identity(self, character: dict):
        """Pretty print character identity.
        
        Args:
            character: Character dictionary
        """
        print("=" * 70)
        print(f"🎭 CHARACTER IDENTITY: {character['name'].upper()}")
        print("=" * 70)
        print(f"\n👤 Age: {character['age']}")
        print(f"\n📖 Background:\n   {character['background']}")
        print(f"\n🎯 Motivation:\n   {character['motivation']}")
        print(f"\n✨ Personality:\n   {', '.join(character['personality'])}")
        print(f"\n💪 Skills:\n   {', '.join(character['skills'])}")
        print(f"\n⚠️  Weakness:\n   {character['weakness']}")
        print(f"\n👁️  Appearance:\n   {character['appearance']}")
        print("\n" + "=" * 70)
    
    def generate_character_dialogue(self, character: dict, situation: str) -> str:
        """Generate dialogue for a character in a specific situation.
        
        Args:
            character: Character dictionary
            situation: The situation/context
            
        Returns:
            Generated dialogue
        """
        system_instruction = f"""You are roleplaying as {character['name']}.
        
        Character Profile:
        - Background: {character['background']}
        - Personality: {', '.join(character['personality'])}
        - Motivation: {character['motivation']}
        
        Speak in character. Your responses should reflect your personality and background.
        Be authentic and consistent with the character's traits."""
        
        prompt = f"Situation: {situation}\n\nHow do you respond?"
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            )
        )
        
        return response.text


def main():
    """Main execution function."""
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        print("👉 Get your API key from: https://aistudio.google.com/")
        return
    
    print("🚀 Level 0: Identity Generation - Way Back Home")
    print("=" * 70)
    print()
    
    # Initialize generator
    generator = IdentityGenerator(api_key)
    
    # Example 1: Generate a fantasy character
    print("📝 Example 1: Fantasy Character\n")
    character = generator.generate_identity("high fantasy epic")
    generator.print_identity(character)
    
    # Example 2: Generate dialogue
    print("\n\n💬 Example 2: Character in Action\n")
    situation = "You discover an ancient artifact that could save your village, but it belongs to a dangerous warlord."
    print(f"Situation: {situation}\n")
    dialogue = generator.generate_character_dialogue(character, situation)
    print(f"💭 {character['name']} says:\n")
    print(f'   "{dialogue}"\n')
    
    # Example 3: Different theme
    print("\n" + "=" * 70)
    print("📝 Example 3: Sci-Fi Character\n")
    scifi_character = generator.generate_identity("cyberpunk dystopia")
    generator.print_identity(scifi_character)
    
    print("\n\n🎉 Level 0 Complete!")
    print("=" * 70)
    print("\n📚 What You Learned:")
    print("  ✓ System instructions for consistent behavior")
    print("  ✓ JSON-structured outputs")
    print("  ✓ Temperature control for creativity")
    print("  ✓ Character consistency across interactions")
    print("\n🚀 Next Step: Level 1 - Multi-Agent Systems")
    print("   Run: python ../level-1/multi_agent.py")


if __name__ == "__main__":
    main()
