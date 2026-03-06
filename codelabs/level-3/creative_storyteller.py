#!/usr/bin/env python3
"""
Creative Storyteller Agent
NYC AI Hackathon 2026 - Creative Storyteller Track

Mission: Build agents that generate rich, interleaved outputs—
seamlessly mixing text, audio, and visuals into a cohesive narrative flow.

This demonstrates:
- Vision analysis → narrative generation
- Multi-modal content creation (text + structured story)
- Creative synthesis from visual input
- Rich, engaging storytelling
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class CreativeStorytellerAgent:
    """
    Generates rich, multi-layered narratives from images.
    
    Perfect for hackathon projects:
    - Photo story generators
    - Travel memory creators
    - Art interpreters
    - Scene-to-screenplay converters
    """
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'
        
        self.storyteller_instruction = """You are a master storyteller who creates rich, engaging narratives from images.

Your creative approach:
1. OBSERVE deeply - notice details others miss
2. IMAGINE possibilities - what stories could this tell?
3. WEAVE elements - combine visual details into cohesive narrative
4. ENRICH with layers - add emotion, backstory, future implications
5. CREATE immersive experience - make readers feel present

Narrative styles you can use:
- Adventure: Epic journeys and discoveries
- Mystery: Intrigue and hidden secrets
- Romance: Emotional connections and relationships
- Fantasy: Magical and otherworldly elements
- Documentary: Real-world storytelling
- Poetry: Lyrical and atmospheric

Always:
- Use vivid, sensory language
- Create compelling characters from visual cues
- Build narrative tension and resolution
- Make every detail meaningful
- Leave readers wanting more"""
    
    def generate_rich_story(self, image_path: str, style: str = "adventure") -> Dict:
        """
        Generate a rich, multi-layered story from an image.
        
        Args:
            image_path: Path to the image
            style: Narrative style (adventure, mystery, romance, fantasy, documentary, poetry)
            
        Returns:
            Dict with story components: title, narrative, characters, mood, themes
        """
        print(f"\n📸 Analyzing image: {os.path.basename(image_path)}")
        print(f"🎨 Style: {style.title()}")
        print("✨ Weaving narrative magic...\n")
        
        # Upload image
        uploaded_file = self.client.files.upload(file=image_path)
        
        # Create comprehensive story prompt
        prompt = f"""Analyze this image and create a rich, {style} narrative.

Your response must be a JSON object with these fields:

{{
  "title": "Compelling title (5-8 words)",
  "hook": "Opening line that grabs attention (1 sentence)",
  "narrative": "Main story (3-4 paragraphs, vivid and immersive)",
  "characters": [
    {{"name": "Character name", "role": "Their role in the story", "trait": "Defining characteristic"}}
  ],
  "setting": {{
    "time": "When this takes place",
    "place": "Where this happens",
    "atmosphere": "The mood and feeling"
  }},
  "themes": ["Theme 1", "Theme 2", "Theme 3"],
  "mood": "Overall emotional tone",
  "ending": "Satisfying conclusion or cliffhanger (1-2 sentences)",
  "sequel_hook": "What might happen next? (optional, 1 sentence)"
}}

Make it creative, engaging, and emotionally resonant. Use sensory details.
Output ONLY valid JSON, no other text."""
        
        # Generate story
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[uploaded_file, prompt],
            config=types.GenerateContentConfig(
                system_instruction=self.storyteller_instruction,
                temperature=0.9,  # High creativity
                response_mime_type="application/json"
            )
        )
        
        story_data = json.loads(response.text)
        
        return story_data
    
    def print_story(self, story: Dict):
        """Print the story in a beautiful format."""
        
        print("═" * 70)
        print(f"  📖 {story['title'].upper()}")
        print("═" * 70)
        
        print(f"\n💫 {story['hook']}\n")
        
        print("📝 THE STORY")
        print("─" * 70)
        print(f"{story['narrative']}\n")
        
        if story.get('characters'):
            print("👥 CHARACTERS")
            print("─" * 70)
            for char in story['characters']:
                print(f"  • {char['name']} - {char['role']}")
                print(f"    {char['trait']}")
            print()
        
        print("🎭 SETTING")
        print("─" * 70)
        setting = story['setting']
        print(f"  When: {setting['time']}")
        print(f"  Where: {setting['place']}")
        print(f"  Atmosphere: {setting['atmosphere']}\n")
        
        print("🎨 THEMES & MOOD")
        print("─" * 70)
        print(f"  Themes: {', '.join(story['themes'])}")
        print(f"  Mood: {story['mood']}\n")
        
        print("✨ ENDING")
        print("─" * 70)
        print(f"{story['ending']}\n")
        
        if story.get('sequel_hook'):
            print("🔮 WHAT'S NEXT?")
            print("─" * 70)
            print(f"{story['sequel_hook']}\n")
        
        print("═" * 70)
    
    def create_multi_chapter_story(self, image_paths: List[str]) -> Dict:
        """
        Create a connected multi-chapter story from multiple images.
        
        Args:
            image_paths: List of image paths (2-5 images work best)
            
        Returns:
            Dict with overall story arc and individual chapters
        """
        print(f"\n📚 Creating multi-chapter story from {len(image_paths)} images...")
        
        chapters = []
        
        # Generate individual chapters
        for i, image_path in enumerate(image_paths, 1):
            print(f"\n📖 Chapter {i}/{len(image_paths)}")
            
            uploaded_file = self.client.files.upload(file=image_path)
            
            prompt = f"""This is image {i} of {len(image_paths)} in a story sequence.

Create a story chapter with:
- Clear beginning/middle/end
- Connection points for next chapter
- Vivid sensory details
- Character development

Provide as JSON:
{{
  "chapter_title": "Title",
  "chapter_text": "2-3 paragraphs",
  "key_moment": "What happens here?",
  "transition": "How does this lead to the next chapter?"
}}

Output ONLY valid JSON."""
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(
                    system_instruction=self.storyteller_instruction,
                    temperature=0.9,
                    response_mime_type="application/json"
                )
            )
            
            chapter = json.loads(response.text)
            chapter['chapter_number'] = i
            chapter['image'] = os.path.basename(image_path)
            chapters.append(chapter)
        
        # Create overall story arc
        print("\n🎬 Weaving chapters into cohesive narrative...")
        
        return {
            'title': f"A Story in {len(image_paths)} Acts",
            'chapters': chapters,
            'chapter_count': len(image_paths)
        }
    
    def create_visual_poem(self, image_path: str) -> str:
        """
        Create a poetic interpretation of an image.
        
        Args:
            image_path: Path to image
            
        Returns:
            Poem text
        """
        print(f"\n🎭 Crafting visual poem...")
        
        uploaded_file = self.client.files.upload(file=image_path)
        
        prompt = """Create a beautiful poem inspired by this image.

Requirements:
- 3-4 stanzas, 4 lines each
- Use vivid imagery and metaphor
- Capture the mood and essence
- Make it emotionally resonant

Just output the poem, nothing else."""
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[uploaded_file, prompt],
            config=types.GenerateContentConfig(
                system_instruction=self.storyteller_instruction,
                temperature=1.0
            )
        )
        
        return response.text


def demo_single_story(agent: CreativeStorytellerAgent, image_path: str):
    """Demo: Generate a rich story from single image."""
    
    print("\n" + "═" * 70)
    print("  🎨 CREATIVE STORYTELLER DEMO")
    print("  Single Image → Rich Narrative")
    print("═" * 70)
    
    # Try different styles
    styles = ['adventure', 'mystery', 'fantasy']
    
    for style in styles:
        print(f"\n\n{'='*70}")
        print(f"  Style: {style.upper()}")
        print("=" * 70)
        
        story = agent.generate_rich_story(image_path, style=style)
        agent.print_story(story)
        
        input("\nPress Enter for next style...")


def demo_poem(agent: CreativeStorytellerAgent, image_path: str):
    """Demo: Create a poem from image."""
    
    print("\n" + "═" * 70)
    print("  🎭 VISUAL POETRY")
    print("═" * 70)
    
    poem = agent.create_visual_poem(image_path)
    
    print("\n" + "─" * 70)
    print(poem)
    print("─" * 70)


def main():
    """Main demo function."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found")
        return
    
    # Find sample image
    sample_dir = Path(__file__).parent.parent.parent / "examples" / "vision-agent" / "samples"
    if sample_dir.exists():
        sample_images = list(sample_dir.glob("*.jpg")) + list(sample_dir.glob("*.png"))
        if sample_images:
            image_path = str(sample_images[0])
        else:
            print("❌ No sample images found")
            return
    else:
        print("❌ No samples directory found")
        print("💡 Usage: python creative_storyteller.py --image path/to/image.jpg")
        return
    
    print(f"\n📸 Using image: {os.path.basename(image_path)}")
    
    agent = CreativeStorytellerAgent(api_key)
    
    print("\n" + "═" * 70)
    print("  🌟 NYC AI HACKATHON 2026")
    print("  Creative Storyteller Track")
    print("═" * 70)
    print("\n📖 Choose demo:")
    print("  1. Rich Story (adventure/mystery/fantasy)")
    print("  2. Visual Poem")
    print("  3. Both\n")
    
    choice = input("Your choice (1/2/3): ").strip()
    
    if choice == '1':
        demo_single_story(agent, image_path)
    elif choice == '2':
        demo_poem(agent, image_path)
    elif choice == '3':
        demo_single_story(agent, image_path)
        demo_poem(agent, image_path)
    else:
        print("Running full demo...")
        demo_single_story(agent, image_path)
    
    print("\n\n" + "═" * 70)
    print("  ✨ CREATIVE STORYTELLER - COMPLETE!")
    print("═" * 70)
    
    print("\n💡 Hackathon Project Ideas:")
    print("\n1. 📸 **Instant Photo Stories**")
    print("   - Take photo → Get creative story")
    print("   - Multiple narrative styles")
    print("   - Social media ready\n")
    
    print("2. 🎨 **Art Narrative Generator**")
    print("   - Analyze artwork → Create backstory")
    print("   - Museum audio guide")
    print("   - Educational + entertaining\n")
    
    print("3. ✈️ **Travel Memory Book**")
    print("   - Travel photos → Diary entries")
    print("   - Poetic descriptions")
    print("   - Shareable memories\n")
    
    print("4. 👶 **Kids Story Creator**")
    print("   - Child's drawing → Bedtime story")
    print("   - Educational themes")
    print("   - Parent approved!\n")
    
    print("5. 🎬 **Scene-to-Screenplay**")
    print("   - Photo → Movie scene")
    print("   - Dialogue + stage directions")
    print("   - Hollywood dreams!\n")
    
    print("═" * 70)
    print("\n🎯 Next Steps:")
    print("  • Add audio narration (text-to-speech)")
    print("  • Generate accompanying visuals")
    print("  • Create web interface")
    print("  • Add user story preferences")
    print("  • Build social sharing\n")
    
    print("🏆 Remember: \"Build an experience that creates!\"")
    print("   Not just text—build a complete narrative experience.\n")


if __name__ == "__main__":
    main()
