"""
Vision Agent - Analyzes photos to understand moments
"""

from google import genai
from PIL import Image


class VisionAgent:
    """Analyzes single or multiple photos using Gemini vision"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
    
    def analyze(self, image_paths: list[str] | str, context: str = "") -> str:
        """
        Analyze photo(s) to understand the moment
        
        Args:
            image_paths: Single path or list of paths to photos
            context: Optional parent context
        
        Returns:
            Analysis text describing the moment(s)
        """
        # Handle single photo or multiple
        if isinstance(image_paths, str):
            image_paths = [image_paths]
        
        # Load images
        images = [Image.open(path) for path in image_paths]
        
        # Create prompt based on photo count
        if len(images) == 1:
            prompt = self._single_photo_prompt(context)
        else:
            prompt = self._multiple_photos_prompt(len(images), context)
        
        # Build multimodal content: [img1, img2, ..., prompt]
        content = images + [prompt]
        
        # Call Gemini vision API
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=content
        )
        
        return response.text
    
    def _single_photo_prompt(self, context: str) -> str:
        """Prompt for analyzing a single photo"""
        return f"""Analyze this photo of a child's moment.

Context: {context if context else "A moment worth remembering"}

Describe:
- What activity or moment is happening
- The setting and environment
- Emotions visible (joy, focus, courage, etc.)
- What makes this moment special

Be specific and observant. Focus on details that matter."""
    
    def _multiple_photos_prompt(self, count: int, context: str) -> str:
        """Prompt for analyzing multiple photos"""
        return f"""You're viewing {count} photos from a child's day.

Context: {context if context else "A wonderful day"}

Analyze ALL photos together:
- What activities happened throughout the day
- How the moments connect and flow
- Common themes or emotions across moments
- What made this day special as a whole

Create a cohesive narrative weaving all moments together."""
