from google import genai
from pathlib import Path
from PIL import Image

class VisionAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        
    def analyze_achievement(self, image_path: str, context: str = "") -> dict:
        """
        Analyzes an achievement photo
        
        Args:
            image_path: Path to photo
            context: Optional parent context (e.g., "struggled in cocoon")
        
        Returns:
            {
                'activity': 'snowboarding',
                'setting': 'snowy mountain',
                'emotions': 'joy, pride, courage',
                'achievement_type': 'first_time',
                'visual_details': '...'
            }
        """
        # Load image
        img = Image.open(image_path)
        
        # Prompt for vision analysis
        prompt = f"""Analyze this achievement photo. 

Context: {context if context else "A child's achievement moment"}

Identify:
1. What activity/achievement is happening?
2. What's the setting/environment?
3. What emotions do you see?
4. Is this a first attempt, progress, or mastery?
5. What visual details stand out?

Return analysis as structured description."""
        
        # Send to Gemini
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[img, prompt]
        )
        
        return {
            'raw_analysis': response.text,
            'image_path': image_path
        }
    
    def analyze_multiple_moments(self, image_paths, context=""):
        """
        Analyze multiple photos from a day to create a cohesive narrative
        
        Args:
            image_paths: List of paths to photos (chronological order recommended)
            context: Optional context about the day
        
        Returns:
            dict with combined analysis of all moments
        """
        
        # Load all images
        images = [Image.open(path) for path in image_paths]
        
        # Create multi-photo analysis prompt
        prompt = f"""You are viewing {len(images)} photos from a child's day.

Context: {context if context else "A wonderful day of moments"}

Analyze ALL photos together and describe:
- The progression of activities throughout the day
- Common themes or emotions across the moments
- What made this day special
- How these moments connect into a single story

Look at each photo carefully. Create a cohesive narrative that weaves all moments together."""

        # Build multimodal content list: [img1, img2, img3, ..., prompt]
        content = images + [prompt]
        
        # Send to Gemini with multiple images
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=content
        )
        
        return {
            'raw_analysis': response.text,
            'image_paths': image_paths,
            'photo_count': len(image_paths)
        }

# Test function
def test_vision():
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    agent = VisionAgent(api_key)
    
    # Test with placeholder
    print("🔍 Vision Agent Ready!")
    print("📸 Waiting for your son's snowboard photo...")
    print("\nUsage:")
    print("  result = agent.analyze_achievement('path/to/photo.jpg', 'He struggled in his cocoon year')")
    
if __name__ == "__main__":
    test_vision()
