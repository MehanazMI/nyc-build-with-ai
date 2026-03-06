#!/usr/bin/env python3
"""
Vision Agent - Image and Video Analysis with Gemini
Demonstrates multimodal vision capabilities.
"""

import os
import base64
from pathlib import Path
from typing import List, Union
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()


class VisionAgent:
    """AI agent with vision capabilities."""
    
    def __init__(self, api_key: str):
        """Initialize the vision agent.
        
        Args:
            api_key: Google Gemini API key
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'  # Latest stable model
        
    def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail.") -> str:
        """Analyze a single image.
        
        Args:
            image_path: Path to the image file
            prompt: Question or instruction about the image
            
        Returns:
            Analysis result
        """
        print(f"\n👁️  Analyzing image: {os.path.basename(image_path)}")
        print(f"❓ Prompt: {prompt}")
        print("⏳ Processing...\n")
        
        # Upload file
        uploaded_file = self.client.files.upload(file=image_path)
        
        # Generate content
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[uploaded_file, prompt]
        )
        
        return response.text
    
    def compare_images(self, image_paths: List[str], prompt: str) -> str:
        """Compare multiple images.
        
        Args:
            image_paths: List of image file paths
            prompt: Question about the images
            
        Returns:
            Comparison result
        """
        print(f"\n👁️  Comparing {len(image_paths)} images")
        print(f"❓ Prompt: {prompt}")
        print("⏳ Processing...\n")
        
        # Upload all files
        uploaded_files = []
        for img_path in image_paths:
            uploaded_file = self.client.files.upload(file=img_path)
            uploaded_files.append(uploaded_file)
        
        # Generate content with all images and prompt
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=uploaded_files + [prompt]
        )
        
        return response.text
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from an image (OCR).
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text
        """
        prompt = """Extract all text visible in this image.
        Format the text as it appears, preserving structure.
        If no text is visible, say 'No text detected.'"""
        
        return self.analyze_image(image_path, prompt)
    
    def count_objects(self, image_path: str, object_type: str = "objects") -> str:
        """Count specific objects in an image.
        
        Args:
            image_path: Path to the image file
            object_type: Type of object to count
            
        Returns:
            Count and details
        """
        prompt = f"""Count the number of {object_type} in this image.
        Provide:
        1. Total count
        2. Brief description of each
        3. Their positions/locations if relevant"""
        
        return self.analyze_image(image_path, prompt)
    
    def describe_scene(self, image_path: str) -> str:
        """Provide detailed scene description.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Scene description
        """
        prompt = """Analyze this scene comprehensively:
        
        1. Setting: Where is this? Indoor/outdoor? Time of day?
        2. Subjects: Who or what is the main focus?
        3. Actions: What's happening?
        4. Mood: What's the atmosphere or emotion?
        5. Details: Notable objects, colors, patterns?
        6. Context: Any text, signs, or identifying information?
        
        Be specific and descriptive."""
        
        return self.analyze_image(image_path, prompt)
    
    def generate_story(self, image_path: str) -> str:
        """Generate a creative story based on an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Generated story
        """
        prompt = """Create a short, engaging story inspired by this image.
        
        Include:
        - A compelling narrative (200-300 words)
        - Character development if people are present
        - Sensory details (what you see, implied sounds, atmosphere)
        - A beginning, middle, and end
        
        Be creative and immersive!"""
        
        return self.analyze_image(image_path, prompt)


def create_sample_image():
    """Create a simple test image if none exists."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple image
        img = Image.new('RGB', (800, 600), color=(135, 206, 235))  # Sky blue
        draw = ImageDraw.Draw(img)
        
        # Draw sun
        draw.ellipse([650, 50, 750, 150], fill='yellow')
        
        # Draw ground
        draw.rectangle([0, 400, 800, 600], fill='green')
        
        # Draw house
        draw.rectangle([250, 250, 450, 400], fill='red')
        draw.polygon([(250, 250), (350, 150), (450, 250)], fill='brown')
        
        # Draw window
        draw.rectangle([300, 300, 350, 350], fill='lightblue')
        
        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        draw.text((275, 450), "Home Sweet Home", fill='black', font=font)
        
        # Save
        samples_dir = Path("samples")
        samples_dir.mkdir(exist_ok=True)
        img_path = samples_dir / "test_scene.jpg"
        img.save(img_path)
        
        return str(img_path)
    
    except ImportError:
        print("⚠️  PIL/Pillow not installed. Cannot create sample image.")
        print("   Install with: pip install pillow")
        return None


def main():
    """Main execution function."""
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        print("👉 Get your API key from: https://aistudio.google.com/")
        return
    
    print("🚀 Vision Agent - Image & Video Analysis")
    print("=" * 70)
    print()
    
    # Initialize vision agent
    agent = VisionAgent(api_key)
    
    # Check for sample images or create one
    samples_dir = Path("samples")
    sample_images = list(samples_dir.glob("*.jpg")) + list(samples_dir.glob("*.png")) if samples_dir.exists() else []
    
    if not sample_images:
        print("📸 No sample images found. Creating a test image...")
        test_image = create_sample_image()
        if test_image:
            sample_images = [Path(test_image)]
        else:
            print("\n💡 To test the vision agent:")
            print("  1. Create a 'samples' folder in this directory")
            print("  2. Add some .jpg or .png images")
            print("  3. Run this script again")
            return
    
    # Example 1: Detailed scene analysis
    print("\n" + "=" * 70)
    print("📋 EXAMPLE 1: Scene Analysis")
    print("=" * 70)
    
    image_path = str(sample_images[0])
    description = agent.describe_scene(image_path)
    print(f"\n✅ Scene Description:\n{description}")
    
    # Example 2: Extract text (OCR)
    print("\n" + "=" * 70)
    print("📋 EXAMPLE 2: Text Extraction (OCR)")
    print("=" * 70)
    
    text = agent.extract_text(image_path)
    print(f"\n✅ Extracted Text:\n{text}")
    
    # Example 3: Custom analysis
    print("\n" + "=" * 70)
    print("📋 EXAMPLE 3: Custom Question")
    print("=" * 70)
    
    custom_result = agent.analyze_image(
        image_path,
        "What emotions or mood does this image evoke? Why?"
    )
    print(f"\n✅ Analysis:\n{custom_result}")
    
    # Example 4: Creative story (Creative Storyteller track)
    print("\n" + "=" * 70)
    print("📋 EXAMPLE 4: Story Generation (Creative Storyteller)")
    print("=" * 70)
    
    story = agent.generate_story(image_path)
    print(f"\n✅ Generated Story:\n{story}")
    
    # If multiple images exist, demonstrate comparison
    if len(sample_images) > 1:
        print("\n" + "=" * 70)
        print("📋 EXAMPLE 5: Multi-Image Comparison")
        print("=" * 70)
        
        comparison = agent.compare_images(
            [str(img) for img in sample_images[:2]],
            "Compare these images. What are the similarities and differences?"
        )
        print(f"\n✅ Comparison:\n{comparison}")
    
    # Summary
    print("\n\n🎉 Vision Agent Demo Complete!")
    print("=" * 70)
    print("\n📚 What You Learned:")
    print("  ✓ Image analysis and description")
    print("  ✓ Text extraction (OCR)")
    print("  ✓ Scene understanding")
    print("  ✓ Creative content generation from images")
    print("  ✓ Multi-image comparison")
    
    print("\n🚀 Ideas for Your Hackathon Project:")
    print("=" * 70)
    print("\n🎤 Live Agent Track:")
    print("  • Visual accessibility assistant")
    print("  • Real-time scene narrator")
    print("  • AR tour guide with image recognition")
    print("  • Safety/hazard detection system")
    
    print("\n✨ Creative Storyteller Track:")
    print("  • Photo-to-story generator")
    print("  • Comic book creator from images")
    print("  • Visual poetry generator")
    print("  • Automated photo album narration")
    
    print("\n💡 Next Steps:")
    print("  1. Add your own images to test")
    print("  2. Try video frame analysis")
    print("  3. Combine with voice agent for multimodal experience")
    print("  4. Build your hackathon project!")


if __name__ == "__main__":
    main()
