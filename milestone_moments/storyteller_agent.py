from google import genai
from pathlib import Path
import re

class ButterflyStorytellerAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        
    def generate_butterfly_story(
        self, 
        vision_analysis: str,
        parent_context: str,
        child_name: str = "Champion"
    ) -> dict:
        """
        Generates butterfly transformation story
        
        Args:
            vision_analysis: Output from VisionAgent
            parent_context: "struggled in cocoon" etc.
            child_name: Child's name or "Champion"
        
        Returns:
            {
                'story': '...',
                'badge_title': 'Butterfly Warrior',
                'badge_subtitle': 'From Cocoon to Flight',
                'next_challenge': '...',
                'dedication': 'To Mom, who held hope...'
            }
        """
        
        prompt = f"""You are a master storyteller celebrating childhood transformations.

VISION ANALYSIS:
{vision_analysis}

PARENT'S CONTEXT:
"{parent_context}"

CREATE A SIMPLE, POWERFUL BUTTERFLY TRANSFORMATION STORY:

WRITING STYLE:
- Short sentences (10-15 words max)
- Simple words a child could understand
- Direct emotion - no flowery language
- 200-250 words total
- Make every sentence count

BUTTERFLY METAPHOR:
- Cocoon = the hard time
- Transformation = getting stronger
- Flight = THIS moment of triumph

STRUCTURE:
1. The cocoon (2-3 short sentences)
2. Mom's hope (1-2 sentences)
3. The transformation (2-3 sentences)
4. THIS moment - the flight! (4-5 sentences describing the photo with awe)
5. The future (1-2 sentences)

TONE: Like a proud parent talking directly to their child
- "You did this"
- "Look at you"
- "Remember when..."

Child's name: {child_name}

Generate the story formatted like this:

🦋 ACHIEVEMENT STORY:
[Write the 200-250 word narrative with short, powerful sentences]

🏆 BADGE TITLE: [2-3 words with emoji]
BADGE SUBTITLE: [Simple transformation phrase]

🔮 NEXT ADVENTURE: [One simple sentence]

💙 DEDICATED TO: [One simple sentence for mom]"""

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        return {
            'full_output': response.text,
            'story_text': response.text,
            'generated_at': 'March 4, 2026'
        }
    
    def narrate_story(self, story_text: str, output_path: str = None) -> str:
        """
        Convert story to audio narration
        
        Args:
            story_text: The story to narrate
            output_path: Path to save audio file (optional)
        
        Returns:
            Path to saved audio file
        """
        try:
            # Extract just the main story text (remove badge/metadata)
            # Get everything between "ACHIEVEMENT STORY:" and the next section
            story_match = re.search(r'🦋 ACHIEVEMENT STORY:\s*(.*?)(?=🏆|$)', story_text, re.DOTALL)
            if story_match:
                clean_story = story_match.group(1).strip()
            else:
                # Fallback: use first few paragraphs
                paragraphs = [p.strip() for p in story_text.split('\n\n') if p.strip() and not p.strip().startswith('🏆')]
                clean_story = '\n\n'.join(paragraphs[:4])  # First 4 paragraphs
            
            # Add gentle opening and closing
            narration_text = f"{clean_story}"
            
            # Generate audio using Gemini text-to-speech
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[{
                    'parts': [{
                        'text': f"Read this story aloud in a warm, gentle, and inspiring voice:\n\n{narration_text}"
                    }]
                }],
                config={
                    'response_modalities': ['AUDIO']
                }
            )
            
            # Save audio if path provided
            if output_path and hasattr(response, 'audio'):
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(response.audio)
                return output_path
            
            return None
            
        except Exception as e:
            print(f"\n⚠️  Audio narration not available: {e}")
            print("   (Text-to-speech requires Google Cloud credits)")
            return None

# Test
def test_storyteller():
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    agent = ButterflyStorytellerAgent(api_key)
    
    # Test with sample data
    sample_vision = "Child snowboarding, winter mountain, joy and pride visible, first-time achievement"
    sample_context = "His first year was the cocoon - dark and difficult. His mom held hope through every moment."
    
    print("✨ Generating butterfly story...")
    print("(This will use 1 API call)\n")
    
    result = agent.generate_butterfly_story(sample_vision, sample_context, "Warrior")
    
    print("\n" + "="*70)
    print(result['full_output'])
    print("="*70)
    print("\n✅ Story generation successful!")

if __name__ == "__main__":
    test_storyteller()
