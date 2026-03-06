"""
Bedtime Stories AI - Main Application

Transform photos into personalized bedtime stories with audio narration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from agents import VisionAgent, StorytellerAgent


class BedtimeStoriesApp:
    """Main application orchestrating the story generation pipeline"""
    
    def __init__(self):
        """Initialize agents with API key"""
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. "
                "Copy .env.example to .env and add your API key."
            )
        
        self.vision = VisionAgent(api_key)
        self.storyteller = StorytellerAgent(api_key)
        print("✅ Bedtime Stories AI ready!\n")
    
    def generate(
        self,
        photo_paths: str | list[str],
        child_name: str,
        context: str = "",
        save_audio: bool = True
    ) -> dict:
        """
        Generate bedtime story from photo(s)
        
        Args:
            photo_paths: Single path or list of photo paths
            child_name: Child's name
            context: Optional parent context
            save_audio: Whether to generate audio narration
        
        Returns:
            {
                'story': str,
                'word_count': int,
                'audio_path': str | None,
                'saved_to': str
            }
        """
        # Ensure photo_paths is a list
        if isinstance(photo_paths, str):
            photo_paths = [photo_paths]
        
        photo_count = len(photo_paths)
        print(f"📸 Analyzing {photo_count} photo(s)...")
        
        # Step 1: Analyze photo(s)
        vision_analysis = self.vision.analyze(photo_paths, context)
        print("✅ Vision analysis complete\n")
        
        # Step 2: Generate story
        print(f"✨ Creating bedtime story for {child_name}...")
        story_result = self.storyteller.create_story(
            vision_analysis=vision_analysis,
            child_name=child_name,
            photo_count=photo_count,
            context=context
        )
        print(f"✅ Story generated ({story_result['word_count']} words)\n")
        
        # Step 3: Generate audio (optional)
        audio_path = None
        if save_audio:
            print("🎵 Generating audio narration...")
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            
            audio_path = self.storyteller.create_audio(
                story_result['story'],
                str(output_dir / f"{child_name.lower()}_bedtime.mp3")
            )
            if audio_path:
                print(f"✅ Audio saved: {audio_path}\n")
        
        # Step 4: Save text story
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        story_file = output_dir / f"{child_name.lower()}_story.txt"
        
        with open(story_file, 'w', encoding='utf-8') as f:
            f.write(f"🌙 Bedtime Story for {child_name} 🌙\n")
            f.write("=" * 60 + "\n\n")
            f.write(story_result['story'])
            f.write("\n\n" + "=" * 60 + "\n")
            
            # Add metadata
            f.write(f"\nPhotos: {', '.join(photo_paths)}\n")
            if context:
                f.write(f"Context: {context}\n")
            f.write(f"Word count: {story_result['word_count']}\n")
        
        print(f"✅ Story saved: {story_file}\n")
        
        return {
            'story': story_result['story'],
            'word_count': story_result['word_count'],
            'audio_path': audio_path,
            'saved_to': str(story_file)
        }
    
    def interactive(self):
        """Interactive mode for demo/testing"""
        print("=" * 60)
        print("🌙 BEDTIME STORIES AI")
        print("=" * 60)
        print("\nTransform photos into personalized bedtime stories!\n")
        
        # Get inputs
        photo_input = input("📸 Photo path(s) [comma-separated]: ").strip()
        
        if not photo_input:
            print("\n🧪 Demo mode: Using sample data...")
            self._demo_mode()
            return
        
        # Parse photo paths
        photo_paths = [p.strip() for p in photo_input.split(',')]
        
        child_name = input("👶 Child's name: ").strip()
        if not child_name:
            child_name = "Little One"
        
        context = input("💭 Context (optional, press Enter to skip): ").strip()
        
        # Generate story
        print("\n🚀 Generating bedtime story...\n")
        
        try:
            result = self.generate(photo_paths, child_name, context)
            
            # Display result
            print("\n" + "=" * 60)
            print("🌙 YOUR BEDTIME STORY")
            print("=" * 60 + "\n")
            print(result['story'])
            print("\n" + "=" * 60)
            
            if result['audio_path']:
                print(f"\n🎵 Audio: {result['audio_path']}")
            print(f"📄 Text: {result['saved_to']}")
            print(f"\n✨ Perfect for tonight's bedtime! Sweet dreams, {child_name}! 🌙\n")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
    
    def _demo_mode(self):
        """Demo mode with simulated data"""
        child_name = "Luna"
        
        # Simulate story generation
        demo_story = f"""Luna, do you remember today at the playground?
You stood at the bottom of that tall slide.
You looked up. It was so high.
Your hands felt sweaty. Your heart beat fast.

But you climbed those steps. One by one.
At the top, you took a deep breath.
Then whoosh! Down you went!

Pure joy lit up your face, Luna.
That's what being brave looks like.
First nervous, then soaring!

Tonight, as you close your eyes, remember:
You were scared. You did it anyway.
That's courage. That's you, Luna.

Dream of tomorrow's adventures.
Sweet dreams, brave one."""
        
        # Save demo story
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        story_file = output_dir / "demo_story.txt"
        
        with open(story_file, 'w', encoding='utf-8') as f:
            f.write(f"🌙 Demo Bedtime Story for {child_name} 🌙\n")
            f.write("=" * 60 + "\n\n")
            f.write(demo_story)
            f.write("\n\n" + "=" * 60 + "\n")
            f.write(f"Word count: {len(demo_story.split())}\n")
        
        print("\n" + "=" * 60)
        print(demo_story)
        print("=" * 60)
        print(f"\n✅ Demo story saved: {story_file}\n")


def main():
    """Main entry point"""
    try:
        app = BedtimeStoriesApp()
        app.interactive()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    main()
