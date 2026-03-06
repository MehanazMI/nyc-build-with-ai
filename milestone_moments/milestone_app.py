from vision_agent import VisionAgent
from storyteller_agent import ButterflyStorytellerAgent
import os
from dotenv import load_dotenv
from pathlib import Path

class MilestoneApp:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        
        self.vision = VisionAgent(api_key)
        self.storyteller = ButterflyStorytellerAgent(api_key)
        
    def create_milestone_story(
        self,
        photo_path: str,
        parent_context: str,
        child_name: str = "Champion"
    ):
        """
        Complete pipeline: photo → analysis → story
        """
        
        print("🦋 MILESTONE MOMENTS - Butterfly Transformation\n")
        
        # Step 1: Vision
        print("📸 Step 1: Analyzing achievement photo...")
        vision_result = self.vision.analyze_achievement(photo_path, parent_context)
        print("✅ Vision analysis complete\n")
        
        # Step 2: Story
        print("✨ Step 2: Generating butterfly transformation story...")
        story_result = self.storyteller.generate_butterfly_story(
            vision_result['raw_analysis'],
            parent_context,
            child_name
        )
        print("✅ Story generated\n")
        
        # Step 3: Audio Narration
        print("🎵 Step 3: Creating audio narration...")
        audio_path = None
        try:
            output_dir = Path("demo_outputs")
            output_dir.mkdir(exist_ok=True)
            audio_file = output_dir / f"butterfly_story_{child_name.lower()}.mp3"
            
            audio_path = self.storyteller.narrate_story(
                story_result['story_text'], 
                str(audio_file)
            )
            
            if audio_path:
                print(f"✅ Audio narration saved: {audio_file}\n")
            else:
                print("⚠️  Audio narration skipped (requires Google Cloud credits)\n")
        except Exception as e:
            print(f"⚠️  Audio narration skipped: {e}\n")
        
        # Display
        print("="*70)
        print("🦋 YOUR BUTTERFLY TRANSFORMATION STORY")
        print("="*70)
        print(story_result['full_output'])
        print("="*70)
        
        # Save to file
        output_dir = Path("demo_outputs")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"butterfly_story_{child_name.lower()}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("🦋 MILESTONE MOMENTS - Butterfly Transformation Story\n")
            f.write("="*70 + "\n\n")
            f.write(f"Photo: {photo_path}\n")
            f.write(f"Context: {parent_context}\n")
            f.write(f"Child: {child_name}\n")
            if audio_path:
                f.write(f"Audio: {audio_path}\n")
            f.write("\n" + story_result['full_output'])
            f.write("\n\n" + "="*70)
        
        print(f"\n💾 Story saved to: {output_file}")
        if audio_path:
            print(f"🎵 Audio saved to: {audio_path}")
            print("\n🎧 Mz can now HEAR his butterfly story!")
        
        return story_result

# Demo
def demo():
    app = MilestoneApp()
    
    print("="*70)
    print("🎯 MILESTONE MOMENTS MVP")
    print("Transforming achievement photos into butterfly stories")
    print("="*70)
    print()
    
    # Get user input
    print("📸 PHOTO SETUP:")
    photo_path = input("   Path to achievement photo (or press Enter for test mode): ").strip()
    
    if not photo_path or not os.path.exists(photo_path):
        print("\n⚠️  Photo not found or test mode selected.")
        print("   Using sample data for demo...\n")
        
        # Test mode - just storyteller
        from storyteller_agent import ButterflyStorytellerAgent
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        
        storyteller = ButterflyStorytellerAgent(api_key)
        
        print("💬 CONTEXT SETUP:")
        context = input("   Brief context (or press Enter for default): ").strip()
        if not context:
            context = "His first year was the cocoon - dark and difficult. His mom held hope through every moment."
        
        name = input("\n👶 CHILD'S NAME (or press Enter for 'Warrior'): ").strip()
        if not name:
            name = "Warrior"
        
        print("\n" + "="*70)
        print("✨ Generating butterfly story (test mode - no photo analysis)...")
        print("="*70 + "\n")
        
        # Sample vision data
        vision_sample = "Child snowboarding on snowy mountain, age 2-3, winter setting, joyful expression, first-time achievement visible, proud stance"
        
        result = storyteller.generate_butterfly_story(vision_sample, context, name)
        
        print("="*70)
        print("🦋 YOUR BUTTERFLY TRANSFORMATION STORY")
        print("="*70)
        print(result['full_output'])
        print("="*70)
        
        # Save
        output_dir = Path("demo_outputs")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"butterfly_story_{name.lower()}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("🦋 MILESTONE MOMENTS - Butterfly Transformation Story\n")
            f.write("="*70 + "\n\n")
            f.write(f"Mode: Test (no photo analysis)\n")
            f.write(f"Context: {context}\n")
            f.write(f"Child: {name}\n\n")
            f.write(result['full_output'])
            f.write("\n\n" + "="*70)
        
        print(f"\n💾 Story saved to: {output_file}")
        print("\n✅ MVP Test Complete!")
        print("\n📝 Next step: Run again with your son's actual snowboard photo!")
        return
    
    # Full pipeline with photo
    print("\n💬 CONTEXT SETUP:")
    context = input("   Brief context about the cocoon year: ").strip()
    if not context:
        context = "His first year was the cocoon - dark and difficult. His mom held hope through every moment."
    
    name = input("\n👶 CHILD'S NAME: ").strip()
    if not name:
        name = "Champion"
    
    print("\n" + "="*70)
    # Generate!
    app.create_milestone_story(photo_path, context, name)
    
    print("\n✅ Complete! Your butterfly story is ready for the hackathon demo! 🦋")

if __name__ == "__main__":
    demo()
