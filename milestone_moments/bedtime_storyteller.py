"""
Bedtime Storyteller Agent
Generates soothing, personalized bedtime stories from daily photos
"""

import google.genai as genai
from pathlib import Path
import re
import os
from dotenv import load_dotenv

load_dotenv()

class BedtimeStorytellerAgent:
    """Agent that creates gentle, personalized bedtime stories from photos"""
    
    def __init__(self):
        """Initialize with Gemini API"""
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_bedtime_story(self, vision_analysis, child_name, additional_context=None, photo_count=1):
        """
        Generate a soothing bedtime story from photo analysis
        
        Args:
            vision_analysis: What AI saw in the photo(s)
            child_name: Child's name for personalization
            additional_context: Optional parent input (voice or text)
            photo_count: Number of photos analyzed (1 for single, 2+ for multiple)
        
        Returns:
            dict with story text and metadata
        """
        
        # Build context-aware prompt
        context_note = ""
        if additional_context:
            context_note = f"\n\nParent's note: {additional_context}"
        
        # Adjust structure based on photo count
        structure_note = ""
        if photo_count > 1:
            structure_note = f"""
IMPORTANT: This story combines {photo_count} moments from today. 
- Weave them together as a flowing journey
- Show progression: "First you..., then you..., and finally..."
- Connect moments with the butterfly theme (flying from moment to moment)
"""
        
        prompt = f"""You are a magical bedtime storyteller. Create a soothing bedtime story for {child_name}.

Based on {"these moments" if photo_count > 1 else "this moment"} from today:
{vision_analysis}{context_note}{structure_note}

STORY REQUIREMENTS:
- Gentle, calming tone perfect for bedtime
- Use simple language (10-15 words per sentence maximum)
- Total length: {"250-300" if photo_count > 1 else "200-250"} words
- Direct address: "You [did/saw/felt] this, {child_name}"
- Weave in the butterfly metaphor: today was like a butterfly's gentle journey
- End with peaceful sleep imagery
- Present tense for immediacy: "You play..." not "You played..."

STRUCTURE:
1. Opening: Gentle acknowledgment of their day
2. Middle: Celebrate the moment{"s" if photo_count > 1 else ""} with butterfly imagery (light, gentle, floating)
3. Closing: Connect to peaceful sleep and dreams

Make it soothing, personal, and perfect for a parent to read aloud as the child drifts to sleep.

Generate the bedtime story now:"""

        try:
            response = self.model.generate_content(prompt)
            story_text = response.text.strip()
            
            return {
                'story': story_text,
                'child_name': child_name,
                'word_count': len(story_text.split()),
                'vision_context': vision_analysis,
                'additional_context': additional_context or "None provided"
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate bedtime story: {str(e)}")
    
    def narrate_story(self, story_text, output_path):
        """
        Convert story to gentle audio narration
        
        Args:
            story_text: The story text to narrate
            output_path: Where to save the audio file
        
        Returns:
            Path to audio file or None if audio generation unavailable
        """
        try:
            # Clean text for better narration
            clean_text = self._prepare_for_narration(story_text)
            
            # Generate soothing audio
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(
                clean_text,
                config={'response_modalities': ['AUDIO']},
            )
            
            # Save audio
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.audio_data)
            
            return str(output_path)
            
        except Exception as e:
            # Graceful degradation - text story still works
            print(f"\nℹ️ Audio narration unavailable: {str(e)}")
            print("💡 Text story generated successfully. Audio requires Google Cloud credits.")
            return None
    
    def _prepare_for_narration(self, story_text):
        """Clean story text for optimal audio narration"""
        # Remove any markdown or special formatting
        clean = re.sub(r'\*\*', '', story_text)
        clean = re.sub(r'\*', '', clean)
        clean = re.sub(r'#{1,6}\s', '', clean)
        
        # Ensure proper pauses with punctuation
        clean = re.sub(r'([.!?])\s+', r'\1 ', clean)
        
        return clean.strip()


if __name__ == "__main__":
    # Test the bedtime storyteller
    storyteller = BedtimeStorytellerAgent()
    
    test_vision = """
    A young child playing with colorful blocks on a sunny living room floor.
    Sunlight streams through the window. The child looks focused and happy,
    building a tall tower. Toys scattered around showing an afternoon of play.
    """
    
    result = storyteller.generate_bedtime_story(
        vision_analysis=test_vision,
        child_name="Luna",
        additional_context="She spent all afternoon building towers"
    )
    
    print("\n✨ BEDTIME STORY GENERATED ✨")
    print(f"\nFor: {result['child_name']}")
    print(f"Word count: {result['word_count']}")
    print("\n" + "="*60)
    print(result['story'])
    print("="*60)
