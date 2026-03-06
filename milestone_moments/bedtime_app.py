"""
Bedtime Story Generator - Main Application
Transform daily photos into personalized bedtime stories
"""

from vision_agent import VisionAgent
from bedtime_storyteller import BedtimeStorytellerAgent
from pathlib import Path
from PIL import Image

class BedtimeStoryApp:
    """Main app orchestrating photo → bedtime story pipeline"""
    
    def __init__(self):
        """Initialize the multimodal AI agents"""
        print("🌙 Initializing Bedtime Story Generator...")
        self.vision = VisionAgent()
        self.storyteller = BedtimeStorytellerAgent()
        print("✅ Ready to create magical bedtime stories!\n")
    
    def create_bedtime_story(self, photo_paths, child_name, additional_context=None):
        """
        Generate personalized bedtime story from photo(s)
        
        Args:
            photo_paths: Single path (str) or list of paths to photos from today
            child_name: Child's name for personalization
            additional_context: Optional parent note (can be None)
        
        Returns:
            dict with story, audio path, and metadata
        """
        
        # Handle single photo or multiple photos
        if isinstance(photo_paths, str):
            photo_paths = [photo_paths]
        
        photo_count = len(photo_paths)
        moment_word = "moments" if photo_count > 1 else "moment"
        
        print(f"📸 Analyzing {child_name}'s {photo_count} {moment_word}...")
        
        # Stage 1: Vision analysis (multimodal)
        vision_context = "a moment from today worth celebrating" if not additional_context else additional_context
        
        if photo_count == 1:
            vision_result = self.vision.analyze_achievement(photo_paths[0], vision_context)
        else:
            vision_result = self.vision.analyze_multiple_moments(photo_paths, vision_context)
        
        print(f"✅ Vision analysis complete")
        
        # Stage 2: Generate bedtime story
        print(f"✨ Creating personalized bedtime story...")
        story_result = self.storyteller.generate_bedtime_story(
            vision_analysis=vision_result['raw_analysis'],
            child_name=child_name,
            additional_context=additional_context,
            photo_count=photo_count
        )
        print(f"✅ Story generated ({story_result['word_count']} words)")
        
        # Stage 3: Generate audio narration
        print("🎵 Generating soothing audio narration...")
        output_dir = Path("demo_outputs")
        output_dir.mkdir(exist_ok=True)
        
        audio_path = self.storyteller.narrate_story(
            story_result['story'],
            output_dir / f"{child_name.lower()}_bedtime.mp3"
        )
        
        if audio_path:
            print(f"✅ Audio saved: {audio_path}")
        
        # Save text story
        story_file = output_dir / f"{child_name.lower()}_bedtime_story.txt"
        with open(story_file, 'w', encoding='utf-8') as f:
            f.write(f"🌙 Bedtime Story for {child_name} 🌙\n")
            f.write("="*60 + "\n\n")
            f.write(story_result['story'])
            f.write("\n\n" + "="*60 + "\n")
            if photo_count == 1:
                f.write(f"\nPhoto: {photo_paths[0]}\n")
            else:
                f.write(f"\nPhotos ({photo_count}):\n")
                for i, path in enumerate(photo_paths, 1):
                    f.write(f"  {i}. {path}\n")
            if additional_context:
                f.write(f"Context: {additional_context}\n")
            f.write(f"Word count: {story_result['word_count']}\n")
        
        print(f"✅ Story saved: {story_file}\n")
        
        return {
            'story': story_result['story'],
            'audio_path': audio_path,
            'story_file': str(story_file),
            'child_name': child_name,
            'word_count': story_result['word_count']
        }
    
    def demo(self):
        """Interactive demo mode"""
        print("\n" + "="*60)
        print("🌙 BEDTIME STORY GENERATOR - Demo Mode 🌙")
        print("="*60 + "\n")
        print("Transform photo(s) from today into a personalized bedtime story!\n")
        
        # Get inputs
        print("📸 Photo path(s):")
        print("   - Single photo: path/to/photo.jpg")
        print("   - Multiple photos: path1.jpg, path2.jpg, path3.jpg")
        print("   - Or press Enter for test mode\n")
        photo_input = s = ["test_photo.jpg"]
            child_name = "Luna"
            additional_context = None
            photo_count = 1
            print("\n🧪 Test mode: Using sample data...")
            photo_path = "test_photo.jpg"
            child_name = "Luna"
            additional_context = None
            
            # Simulate vision analysis for test
            self.vision = None  # Skip actual vision call
            test_vision = "Child playing with colorful blocks, building a tower, happy and focused"
            
            print(f"✨ Creating bedtime story for {child_name}...")
            story_result = self.storyteller.generate_bedtime_story(
                vision_analysis=test_vision,
                child_name=child_name,,
                photo_count=photo_count
                additional_context=additional_context
            )
            
            output_dir = Path("demo_outputs")
            output_dir.mkdir(exist_ok=True)
            story_file = output_dir / f"{child_name.lower()}_bedtime_story.txt"
            
            with open(story_file, 'w', encoding='utf-8') as f:
                f.write(f"🌙 Bedtime Story for {child_name} 🌙\n")
                f.write("="*60 + "\n\n")
                f.write(story_result['story'])
                f.write("\n\n" + "="*60 + "\n")
                f.write(f"Word count: {story_result['word_count']}\n")
            
            print("\n" + "="*60)
            print(story_result['story'])
            print("="*60 + "\n")
            print(f"✅ Saved to: {story_file}\n")
            return
        # Parse photo paths (handle comma-separated list)
        photo_paths = [p.strip() for p in photo_input.split(',')]
        print(f"\n📸 Processing {len(photo_paths)} photo(s)")
        
        child_name = input("👶 Child's name: ").strip()
        
        print("\n💭 Additional context? (Optional - press Enter to skip)")
        if len(photo_paths) > 1:
            print("   Example: 'Morning at park, then baking at home'")
        else:
            print("   Examples: 'First time riding bike' or 'Made this at school'")
        additional_context = input("   Context: ").strip() or None
        
        print("\n🚀 Starting bedtime story generation...\n")
        
        try:
            result = self.create_bedtime_story(photo_paths
            result = self.create_bedtime_story(photo_path, child_name, additional_context)
            
            print("\n" + "="*60)
            print("🌙 YOUR BEDTIME STORY 🌙")
            print("="*60 + "\n")
            print(result['story'])
            print("\n" + "="*60 + "\n")
            
            if result['audio_path']:
                print(f"🎵 Audio: {result['audio_path']}")
            print(f"📄 Text: {result['story_file']}")
            print(f"\n✨ Perfect for tonight's bedtime! Sweet dreams, {child_name}! 🌙\n")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    app = BedtimeStoryApp()
    app.demo()
