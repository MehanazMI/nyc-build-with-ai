"""
Level 0: Avatar Generator

This module generates your unique space explorer avatar using
multi-turn image generation with Gemini (Nano Banana) for
character consistency across portrait and icon.

=== CODELAB INSTRUCTIONS ===

You will implement three steps in the generate_explorer_avatar() function:

1. MODULE_5_STEP_1_CREATE_CHAT_SESSION
   Create a chat session to maintain character consistency

2. MODULE_5_STEP_2_GENERATE_PORTRAIT
   Generate the explorer portrait with your customizations

3. MODULE_5_STEP_3_GENERATE_ICON
   Generate a consistent map icon using the same chat session

Follow the instructions in the codelab to complete each step.
"""

from google import genai
from google.genai import types
from PIL import Image
import json
import os
import io

# Load configuration from setup (config.json is in project root)
CONFIG_PATH = "../config.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

USERNAME = config["username"]
SUIT_COLOR = config["suit_color"]
APPEARANCE = config["appearance"]

# Initialize the Gemini client for Vertex AI
client = genai.Client(
    vertexai=True,
    project=os.environ.get("GOOGLE_CLOUD_PROJECT", config.get("project_id")),
    location="us-central1"
)


def generate_explorer_avatar() -> dict:
    """
    Generate portrait and icon using multi-turn chat for consistency.

    The key technique here is using a CHAT SESSION rather than independent
    API calls. This allows Gemini to "remember" the character it created
    in the first turn, ensuring the icon matches the portrait.

    Returns:
        dict with portrait_path and icon_path
    """

    # =========================================================================
    # MODULE_5_STEP_1_CREATE_CHAT_SESSION
    # =========================================================================
    # TODO: Create a chat session for multi-turn generation
    #
    # Create a chat session using client.chats.create() with:
    # - model: "gemini-2.5-flash-image" (Nano Banana)
    # - config: GenerateContentConfig with response_modalities=["TEXT", "IMAGE"]
    #
    # Hint: You need to use types.GenerateContentConfig
    # =========================================================================
    # MODULE_5_STEP_1_CREATE_CHAT_SESSION
    # Create a chat session to maintain character consistency across generations.
    # The chat session preserves context between turns, so Gemini "remembers"
    # what it generated and can create consistent variations.
    chat = client.chats.create(
        model="gemini-2.5-flash-image",  # Nano Banana - Gemini with image generation
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"]
        )
    )

    # =========================================================================
    # MODULE_5_STEP_2_GENERATE_PORTRAIT
    # =========================================================================
    # TODO: Generate the explorer portrait
    #
    # 1. Create a portrait_prompt string that includes:
    #    - APPEARANCE, USERNAME, and SUIT_COLOR variables
    #    - Style requirements (digital illustration, white background, etc.)
    #
    # 2. Send the prompt using chat.send_message(portrait_prompt)
    #
    # 3. Extract the image from the response:
    #    - Loop through portrait_response.candidates[0].content.parts
    #    - Find the part where part.inline_data is not None
    #    - Convert to PIL Image: Image.open(io.BytesIO(part.inline_data.data))
    #    - Save to "outputs/portrait.png"
    #
    # 4. Print progress messages for user feedback
    # =========================================================================
    # MODULE_5_STEP_2_GENERATE_PORTRAIT (Photo-based bonus version)
    # First turn: Transform a real photo into a stylized space explorer portrait.
    # The photo gives Gemini the person's actual likeness to preserve.

    # Load and convert the photo to bytes for the API
    photo_path = r"C:\Users\rashe\Pictures\IMG_298_2.jpg"
    user_photo = Image.open(photo_path)
    photo_buffer = io.BytesIO()
    user_photo.save(photo_buffer, format="JPEG")
    photo_bytes = photo_buffer.getvalue()

    portrait_prompt = f"""Transform this person into a stylized space explorer portrait.

PHOTO LIKENESS — THIS IS THE #1 PRIORITY:
- You MUST preserve the EXACT face shape, jawline, chin, and forehead proportions
- Match the EXACT eye shape, eye spacing, nose shape, and lip shape from the photo
- Preserve skin tone, hair color, hair texture, and hairstyle exactly
- Keep any distinctive features (glasses, facial hair, moles, dimples, etc.)
- The final image must be IMMEDIATELY recognizable as this SPECIFIC person
- Do NOT idealize, slim, or beautify the face — keep it true to the photo

STYLE ADDITIONS (without losing likeness):
- Digital illustration style, clean lines, vibrant saturated colors
- Add a futuristic space suit with the name "{USERNAME}" on a shoulder patch
- Suit color: {SUIT_COLOR}
- Background: Pure solid white (#FFFFFF) — no gradients or other elements
- Frame: Head and shoulders, 3/4 view facing slightly left
- Lighting: Soft diffused studio lighting, no harsh shadows
- Art style: Semi-realistic illustrated (NOT heavily cartoonish — keep the real face structure)

If you had to choose between style and likeness, ALWAYS choose likeness.
The white background is essential — the avatar will be composited onto a map."""

    print("🎨 Transforming your photo into an explorer portrait...")

    # Send both the text prompt AND the photo image to Gemini
    portrait_response = chat.send_message([
        portrait_prompt,
        types.Part.from_bytes(data=photo_bytes, mime_type="image/jpeg")
    ])

    # Extract the image from the response.
    portrait_image = None
    for part in portrait_response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_bytes = part.inline_data.data
            portrait_image = Image.open(io.BytesIO(image_bytes))
            portrait_image.save("outputs/portrait.png")
            break

    if portrait_image is None:
        raise Exception("Failed to generate portrait - no image in response")
    print("✓ Portrait generated from your photo!")

    # =========================================================================
    # MODULE_5_STEP_3_GENERATE_ICON
    # =========================================================================
    # TODO: Generate a consistent map icon
    #
    # 1. Create an icon_prompt that asks for the SAME character
    #    - Emphasize consistency: "SAME person, SAME face, SAME suit"
    #    - Request tighter crop (head and shoulders only)
    #    - Request white background and square aspect ratio
    #
    # 2. Send the prompt using chat.send_message(icon_prompt)
    #    - The chat session remembers the character from step 2!
    #
    # 3. Extract and save the icon image to "outputs/icon.png"
    #
    # 4. Print progress messages for user feedback
    # =========================================================================
    # MODULE_5_STEP_3_GENERATE_ICON
    # Second turn: Generate a consistent icon for the map.
    # Because we're in the same chat session, Gemini remembers the character
    # from the portrait and will maintain visual consistency.
    icon_prompt = """Now create a SMALL CIRCULAR BADGE icon of this same character for use as a tiny map marker.

THIS MUST LOOK VERY DIFFERENT FROM THE PORTRAIT:
- EXTREME CLOSE-UP: Only the FACE fills the entire frame — no neck, no shoulders, no suit visible
- The face should fill at least 90% of the image area
- Circular composition: imagine the image will be masked into a circle
- Background: Pure solid white (#FFFFFF)
- Square 1:1 aspect ratio
- Bold, thick outlines around the face for visibility at small sizes (32-64px)
- Slightly simplified details compared to portrait — optimized for tiny display
- Add a thin colored border/ring around the edge in {SUIT_COLOR} color

Same person, same face, same likeness — but this is a BADGE/AVATAR icon, NOT another portrait."""

    print("🖼️  Creating map icon...")
    icon_response = chat.send_message(icon_prompt)

    # Extract the icon image from the response
    icon_image = None
    for part in icon_response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_bytes = part.inline_data.data
            icon_image = Image.open(io.BytesIO(image_bytes))
            break

    if icon_image is None:
        raise Exception("Failed to generate icon - no image in response")

    # Crop to circle and resize to icon dimensions
    icon_size = 256  # Generate at 256px, will display at 64px
    icon_image = icon_image.resize((icon_size, icon_size), Image.LANCZOS)

    # Apply circular mask
    mask = Image.new("L", (icon_size, icon_size), 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, icon_size - 1, icon_size - 1), fill=255)
    icon_image.putalpha(mask)

    icon_image.save("outputs/icon.png")
    print("✓ Icon generated (circular crop applied)!")

    return {
        "portrait_path": "outputs/portrait.png",
        "icon_path": "outputs/icon.png"
    }


if __name__ == "__main__":
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)

    print(f"Generating avatar for {USERNAME}...")
    result = generate_explorer_avatar()
    print(f"✅ Avatar created!")
    print(f"   Portrait: {result['portrait_path']}")
    print(f"   Icon: {result['icon_path']}")
