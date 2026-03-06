# 🦋 Milestone Moments - Butterfly Warrior
## MVP Build Plan - March 4, 2026

**Goal:** Build working prototype in 6 hours that generates butterfly transformation stories from achievement photos.

**Why Build NOW (not wait for GCP credits)?**
- Google Cloud Credits distributed March 7 (7:45 PM) - 3 days away
- Need working prototype to ENHANCE, not build from scratch
- Free Gemini API tier is enough for MVP
- Hackathon Day 1 assumes you have basics working
- Use credits to ADD features, not build foundation

---

## 🎯 TODAY's Build Plan

### Phase 1: Vision Analysis (1.5 hours) ⏰ 9:00-10:30 AM

**Goal:** AI sees the snowboard photo and understands the achievement

**Files to create:**
- `milestone_moments/vision_agent.py`

**Code:**
```python
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
        
        Return analysis as structured JSON."""
        
        # Send to Gemini
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[img, prompt]
        )
        
        return {
            'raw_analysis': response.text,
            'image_path': image_path
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
```

**Test:**
```powershell
cd milestone_moments
python vision_agent.py
```

---

### Phase 2: Story Generation (2 hours) ⏰ 10:30 AM-12:30 PM

**Goal:** AI generates butterfly transformation narrative

**Files to create:**
- `milestone_moments/storyteller_agent.py`

**Code:**
```python
from google import genai

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

CREATE A BUTTERFLY TRANSFORMATION STORY:
- 300-400 words
- Use butterfly metaphor: cocoon (struggle) → transformation → flight
- Emotional, inspiring, celebrating courage
- Acknowledge mom's role in holding hope
- Focus on the triumph visible in the photo

STRUCTURE:
1. Acknowledge the cocoon year (brief, respectful)
2. Celebrate the transformation 
3. Describe THIS moment (the flight!)
4. Look forward (what's next for this butterfly?)

TONE: Warm, proud, hopeful, empowering

Child's name: {child_name}

Generate:
1. Achievement story (300-400 words)
2. Badge title (2-4 words, emoji-worthy)
3. Badge subtitle (transformation focus)
4. Next challenge suggestion
5. Dedication line for mom"""

        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        
        return {
            'full_output': response.text,
            'generated_at': 'March 4, 2026'
        }

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
    result = agent.generate_butterfly_story(sample_vision, sample_context, "Warrior")
    
    print("\n" + "="*60)
    print(result['full_output'])
    print("="*60)

if __name__ == "__main__":
    test_storyteller()
```

**Test:**
```powershell
python storyteller_agent.py
```

---

### Phase 3: Integration (1.5 hours) ⏰ 1:00-2:30 PM

**Files to create:**
- `milestone_moments/milestone_app.py` (main orchestrator)

**Code:**
```python
from vision_agent import VisionAgent
from storyteller_agent import ButterflyStorytellerAgent
import os
from dotenv import load_dotenv

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
        print("📸 Analyzing achievement photo...")
        vision_result = self.vision.analyze_achievement(photo_path, parent_context)
        print("✅ Vision analysis complete\n")
        
        # Step 2: Story
        print("✨ Generating butterfly story...")
        story_result = self.storyteller.generate_butterfly_story(
            vision_result['raw_analysis'],
            parent_context,
            child_name
        )
        print("✅ Story generated\n")
        
        # Display
        print("="*70)
        print("🦋 YOUR BUTTERFLY TRANSFORMATION STORY")
        print("="*70)
        print(story_result['full_output'])
        print("="*70)
        
        return story_result

# Demo
def demo():
    app = MilestoneApp()
    
    print("🎯 MILESTONE MOMENTS MVP")
    print("Transforming achievement photos into butterfly stories\n")
    
    # Get user input
    photo_path = input("📸 Path to achievement photo: ").strip()
    
    if not photo_path or not os.path.exists(photo_path):
        print("❌ Photo not found. Using test mode...")
        photo_path = "test_photo.jpg"  # Will fail gracefully
    
    context = input("💬 Brief context (e.g., 'struggled in his cocoon year'): ").strip()
    if not context:
        context = "A challenging first year, now soaring"
    
    name = input("👶 Child's name (or press Enter for 'Champion'): ").strip()
    if not name:
        name = "Champion"
    
    # Generate!
    app.create_milestone_story(photo_path, context, name)

if __name__ == "__main__":
    demo()
```

---

### Phase 4: Demo Prep (1 hour) ⏰ 2:30-3:30 PM

1. **Generate actual story with snowboard photo**
2. **Save outputs:**
   - Story text → `demo_outputs/butterfly_story.txt`
   - Screenshots → `demo_outputs/screenshots/`
3. **Practice demo** (use DEMO-PRACTICE.md)
4. **Record backup video** (in case API fails during hackathon)

---

## 📁 Project Structure

```
milestone_moments/
├── __init__.py
├── vision_agent.py          # Vision analysis
├── storyteller_agent.py     # Story generation
├── milestone_app.py         # Main orchestrator
├── demo_outputs/            # Pre-generated demos
│   ├── butterfly_story.txt
│   └── screenshots/
└── README.md
```

---

## 🎯 Success Criteria (End of Day)

- [ ] Vision agent analyzes snowboard photo
- [ ] Storyteller generates butterfly narrative
- [ ] Full pipeline works: photo → story
- [ ] Demo outputs saved (backup for hackathon)
- [ ] Practice demo script 3 times
- [ ] Backup video recorded

---

## 🚨 API Rate Limit Management

**You have ~20 requests/day on free tier:**

- Vision analysis: ~1 request per photo
- Story generation: ~1 request per story
- Testing: ~5-10 requests

**Strategy:**
- Test with 1-2 photos today
- Generate final demo content
- Save all outputs as backups
- Don't regenerate unnecessarily

---

## ⏰ Timeline

**9:00 AM** - Start Phase 1 (Vision)  
**10:30 AM** - Start Phase 2 (Story)  
**12:30 PM** - Lunch break  
**1:00 PM** - Start Phase 3 (Integration)  
**2:30 PM** - Start Phase 4 (Demo prep)  
**3:30 PM** - DONE! Rest & practice

**Tomorrow (March 5):** Polish, add visual badge generation, practice demo

---

## 🎤 Remember Your Demo Opening

> "My son is like a butterfly. He struggled in his cocoon. He transformed. Now he flies."
>
> [Show snowboard photo]
>
> "This is him at 2.5 - flying down mountains. I built AI to celebrate transformations that matter."

**You've got this!** 🦋✨
