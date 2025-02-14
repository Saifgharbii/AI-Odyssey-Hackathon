import os
import json
import time
from datetime import datetime
import google.generativeai as genai
from moviepy.editor import VideoFileClip  # For video downscaling
from dotenv import load_dotenv

load_dotenv()
# Configure Gemini
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# Constants
ANALYSIS_FILE = "Analysis\daily_analysis.txt"
ANALYSIS_JSON = "Analysis\analysis_data.json"
FRAME_RATE = 10  # Frames per second for downscaling

def downscale_video(video_path: str, output_path: str, frame_rate: int = FRAME_RATE):
    """
    Downscales a video to the specified frame rate.
    
    Args:
        video_path (str): Path to the input video.
        output_path (str): Path to save the downscaled video.
        frame_rate (int): Target frame rate.
    """
    with VideoFileClip(video_path) as video:
        video = video.set_fps(frame_rate)
        video.write_videofile(output_path, codec="libx264")

def upload_to_gemini(path: str, mime_type: str = None):
    """
    Uploads a file to Gemini and returns the file object.
    """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """
    Waits for uploaded files to become active.
    """
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

def analyze_video(video_path: str, metadata: dict):
    """
    Analyzes a TikTok video using Gemini and saves the results.
    
    Args:
        video_path (str): Path to the video file.
        metadata (dict): Scraped metadata (likes, comments, captions, etc.).
    """
    # Downscale the video
    downscaled_path = "downscaled_video.mp4"
    downscale_video(video_path, downscaled_path)
    
    # Upload the downscaled video to Gemini
    video_file = upload_to_gemini(downscaled_path, mime_type="video/mp4")
    wait_for_files_active([video_file])
    
    # Create the model
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config={
            "temperature": 0.5,
            "top_p": 0.95,
            "max_output_tokens": 2048,
            "response_mime_type": "application/json",
        },
        system_instruction=(
            "You are a TikTok video analyst. Analyze the video and metadata to extract viral elements. "
            "Return a JSON with: "
            "1. viral_elements: A paragraph describing what makes the video viral. "
            "2. recommendations: Suggestions for improving future videos. "
            "3. metadata_summary: A summary of the scraped metadata (likes, comments, captions)."
        )
    )
    
    # Prepare the prompt
    prompt = (
        f"Analyze this TikTok video and its metadata:\n"
        f"Metadata: {json.dumps(metadata)}\n"
        f"Provide insights on what makes it viral and recommendations for improvement."
    )
    
    # Send the prompt to Gemini
    response = model.generate_content([prompt, video_file])
    analysis_result = json.loads(response.text)
    
    # Save the analysis
    save_analysis(analysis_result)

def save_analysis(analysis_result: dict):
    """
    Saves the analysis result to a text file and updates the JSON file.
    
    Args:
        analysis_result (dict): The analysis result from Gemini.
    """
    # Get today's date as the key
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Append to daily text file
    with open(ANALYSIS_FILE, "a") as f:
        f.write(f"\n\n=== Analysis on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        f.write(f"Viral Elements: {analysis_result['viral_elements']}\n")
        f.write(f"Recommendations: {analysis_result['recommendations']}\n")
        f.write(f"Metadata Summary: {analysis_result['metadata_summary']}\n")
    
    # Update JSON file
    if os.path.exists(ANALYSIS_JSON):
        with open(ANALYSIS_JSON, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = {}
    
    # Add analysis to today's entry
    if today not in existing_data:
        existing_data[today] = []
    
    existing_data[today].append({
        "timestamp": datetime.now().isoformat(),
        "analysis": analysis_result
    })
    
    with open(ANALYSIS_JSON, "w") as f:
        json.dump(existing_data, f, indent=2)

# Example Usage
if __name__ == "__main__":
    # Example scraped metadata
    metadata = {
        "likes": 15000,
        "comments": 1200,
        "shares": 800,
        "caption": "This is how you make the perfect coffee! ☕️ #CoffeeLovers",
        "hashtags": ["#CoffeeLovers", "#BaristaLife", "#TikTokFood"]
    }
    
    # Path to the scraped video
    video_path = "tiktok_baamitheultima_7468229111371156742.mp4"
    
    # Analyze the video
    analyze_video(video_path, metadata)