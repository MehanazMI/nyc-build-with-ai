"""
Storyteller Agent - Creates soothing bedtime stories
"""

from google import genai
import re


class StorytellerAgent:
    """Generates personalized bedtime stories with constrained generation"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
    
    def create_story(
        self,
        vision_analysis: str,
        child_name: str,
        photo_count: int = 1,
        context: str = ""
    ) -> dict:
        """
        Create a soothing bedtime story
        
        Args:
            vision_analysis: Output from VisionAgent
            child_name: Child's name for personalization
            photo_count: Number of photos (affects word count)
            context: Optional parent context
        
        Returns:
            {
                'story': str,
                'word_count': int,
                'photo_count': int
            }
        """
        # Determine word count based on photos
        word_count = "200-250" if photo_count == 1 else "250-300"
        
        # Build prompt
        prompt = self._build_prompt(
            vision_analysis, 
            child_name, 
            photo_count, 
            word_count,
            context
        )
        
        # Generate story
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        story = response.text.strip()
        
        return {
            'story': story,
            'word_count': len(story.split()),
            'photo_count': photo_count,
            'child_name': child_name
        }
    
    def create_audio(self, story_text: str, output_path: str) -> str | None:
        """
        Generate audio narration (requires Google Cloud credits)
        
        Args:
            story_text: Story to narrate
            output_path: Where to save audio file
        
        Returns:
            Path to audio file or None if unavailable
        """
        try:
            # Clean text for narration
            clean_text = self._clean_for_audio(story_text)
            
            # Generate audio
            response = self.client.models.generate_content(
                clean_text,
                config={'response_modalities': ['AUDIO']}
            )
            
            # Save audio
            with open(output_path, 'wb') as f:
                f.write(response.audio_data)
            
            return output_path
            
        except Exception as e:
            print(f"\n⚠️  Audio generation unavailable: {str(e)}")
            print("💡 Requires Google Cloud credits (distributed March 7)")
            return None
    
    def _build_prompt(
        self,
        vision: str,
        name: str,
        photo_count: int,
        word_count: str,
        context: str
    ) -> str:
        """Build the storytelling prompt with constraints"""
        
        multi_photo_note = ""
        if photo_count > 1:
            multi_photo_note = f"""
IMPORTANT: This story combines {photo_count} moments.
- Weave them together: "First you..., then you..., finally..."
- Show progression through the day
- Connect moments with gentle transitions
"""
        
        context_note = f"\n\nParent's note: {context}" if context else ""
        
        return f"""You are a magical bedtime storyteller who creates imaginative narratives, not descriptions.

MOMENT(S):
{vision}{context_note}{multi_photo_note}

CREATE AN IMAGINATIVE BEDTIME STORY FOR {name}:

IMPORTANT - TELL A STORY, DON'T DESCRIBE:
- Transform moments into adventures and discoveries
- Use "remember when..." and "imagine..." language
- Focus on feelings, wonder, and small magical details
- Make ordinary moments feel special and meaningful
- Tell what happened before and after the photo

REQUIREMENTS:
- Simple language (10-15 words per sentence maximum)
- Total length: {word_count} words
- Direct address: "You did this, {name}"
- Imaginative yet soothing narrative
- Build emotional connection
- End with peaceful sleep imagery

STRUCTURE:
1. Opening: "Remember today, {name}..." (set the scene)
2. Middle: Tell the story of what happened (adventure, discovery, courage)
3. Closing: "Now it's time to rest..." (connect to sleep)

Create a STORY with heart, not a picture description. Make {name} the hero of their own adventure."""
    
    def _clean_for_audio(self, text: str) -> str:
        """Clean text for optimal audio narration"""
        # Remove markdown formatting
        clean = re.sub(r'\*\*', '', text)
        clean = re.sub(r'\*', '', clean)
        clean = re.sub(r'#{1,6}\s', '', clean)
        
        # Ensure proper pauses
        clean = re.sub(r'([.!?])\s+', r'\1 ', clean)
        
        return clean.strip()
