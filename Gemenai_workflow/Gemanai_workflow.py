import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def create_product_paragraph(product_data: dict) -> str:
    """
    Creates a marketing paragraph from product extraction JSON.
    
    Args:
        product_data (dict): JSON containing product details.
        
    Returns:
        str: A well-formatted marketing paragraph.
    """
    paragraph = (
        f"Introducing the {product_data['product_name']}, designed for {product_data['target_audience'].lower()}. "
        f"{product_data['key_features']} "
        f"{product_data['call_to_action']}"
    )
    return paragraph

# Example Usage
if __name__ == "__main__":
    # Sample JSON from LLM
    product_json = {
        "product_name": "ThunderBuds Pro Wireless Earbuds",
        "key_features": "Enjoy 40-hour battery life, crystal-clear sound quality, and advanced noise cancellation for an immersive audio experience.",
        "target_audience": "Young professionals and fitness enthusiasts",
        "call_to_action": "Upgrade your sound today!"
    }
    
    # Generate the paragraph
    product_paragraph = create_product_paragraph(product_json)
    print(product_paragraph)

# Initialize Gemini
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# System Prompts
PRODUCT_EXTRACTION_PROMPT = """You are a marketing assistant. Extract product details from the input and return a JSON with:
1. product_name: A creative name for the product (5 words max).
2. key_features: A paragraph listing 3-5 main selling points in a natural, flowing sentence.
3. target_audience: A short paragraph describing the primary demographic.
4. call_to_action: A short, actionable phrase (e.g., "Shop now!")."""

CONTENT_CREATION_PROMPT = """You are a viral content creator. Generate content for a 10-second TikTok/X post. Return a JSON with:
1. script: A paragraph with the 10-second narration (120-150 words) and a description of the speaker's tone.
2. audio_prompt: A paragraph describing the voiceover and the speaker's tone for the post that will be combined with the video.
3. video_prompt: A paragraph describing a single-scene video (10s) with product focus and visual style.
4. image_prompt: A paragraph describing a static image for the product post.
5. caption: A single paragraph combining the caption and hashtags (125 chars max)."""

def process_user_input(user_input: str, is_audio: bool = False):
    # Convert audio to text if needed
    if is_audio:
        user_input = speech_to_text(user_input)
    
    # First LLM Call - Product Extraction
    extraction_model = genai.GenerativeModel(
        model_name="gemini-2.0-pro-exp-02-05",
        generation_config={"response_mime_type": "application/json"},
        system_instruction=PRODUCT_EXTRACTION_PROMPT
    )
    product_info = json.loads(extraction_model.start_chat().send_message(user_input).text)
    
    # Get Trend Analysis (Replace with actual API call)
    trends = get_trend_analysis()  # Assume returns string of trending topics
    
    # Second LLM Call - Content Creation
    creation_model = genai.GenerativeModel(
        model_name="gemini-2.0-pro-exp-02-05",
        generation_config={"response_mime_type": "application/json"},
        system_instruction=CONTENT_CREATION_PROMPT.format(trends=trends)
    )
    
    final_content = json.loads(creation_model.start_chat().send_message(
        f"Product details: {json.dumps(product_info)}\nTrend context: {trends}"
    ).text)
    
    return final_content

# Example Usage
if __name__ == "__main__":
    # For audio input
    audio_content = process_user_input("path/to/audio.wav", is_audio=True)
    
    # For text input
    text_content = process_user_input("New wireless headphones with 40hr battery and noise cancellation")
    
    print(json.dumps(text_content, indent=2))