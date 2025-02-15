import os
import json
import time
import requests
import subprocess
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=API_KEY)

# File paths
DAILY_ANALYSIS_TEXT = "Analysis/daily_analysis.txt"
ANALYSIS_JSON_FILE = "Analysis/analysis_data.json"
FRAME_RATE = 10  # Frames per second for downscaling

def process_video(input_path: str, output_path: str, target_frame_rate: int = FRAME_RATE):
    """
    Downscales a video to the specified frame rate using ffmpeg.
    """
    ffmpeg_command = [
        "ffmpeg", "-i", input_path, "-r", str(target_frame_rate), "-c:v", "libx264",
        "-preset", "fast", "-crf", "23", "-y", output_path
    ]
    print("Executing command:", ffmpeg_command)
    subprocess.run(ffmpeg_command, check=True, stdout=subprocess.DEVNULL)

def upload_file_to_gemini(file_path: str, mime_type: str = None):
    """Uploads a file to Gemini and returns the file object."""
    uploaded_file = genai.upload_file(file_path, mime_type=mime_type)
    print(f"Uploaded file '{uploaded_file.display_name}' as: {uploaded_file.uri}")
    return uploaded_file

def wait_for_file_activation(uploaded_files):
    """Waits for uploaded files to become active."""
    print("Waiting for file activation...")
    for file in uploaded_files:
        while (current_file := genai.get_file(file.name)).state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
        if current_file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("All files are active.")

def analyze_tiktok_video(video_path: str, metadata: dict):
    """Analyzes a TikTok video using Gemini and saves the results."""
    downscaled_video = "downscaled_video.mp4"
    process_video(video_path, downscaled_video)

    video_file = upload_file_to_gemini(downscaled_video, mime_type="video/mp4")
    wait_for_file_activation([video_file])

    analysis_model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config={
            "temperature": 0.5,
            "top_p": 0.95,
            "max_output_tokens": 2048,
            "response_mime_type": "application/json",
        },
        system_instruction=(
            "You are a TikTok video analyst. Analyze the video and metadata to identify viral elements. "
            "Provide a JSON response with the following structure: "
            "1. viral_elements: A paragraph describing the video's viral components. "
            "2. recommendations: Suggestions for improving future videos. "
            "3. metadata_summary: A summary of the scraped metadata. "
            "4. topics_and_hashtags: Relevant topics and hashtags."
        )
    )

    prompt = (
        f"Analyze this TikTok video and its metadata:\n"
        f"Metadata: {json.dumps(metadata)}\n"
        f"Identify viral elements and suggest improvements."
    )

    response = analysis_model.generate_content([prompt, video_file])
    analysis_data = json.loads(response.text)
    store_analysis_result(analysis_data)

def store_analysis_result(analysis_data: dict):
    """Saves the analysis result to text and JSON files."""
    current_date = datetime.now().strftime("%Y-%m-%d")

    with open(DAILY_ANALYSIS_TEXT, "a") as text_file:
        text_file.write(f"\n\n=== Analysis on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        text_file.write(f"Viral Elements: {analysis_data['viral_elements']}\n")
        text_file.write(f"Recommendations: {analysis_data['recommendations']}\n")
        text_file.write(f"Metadata Summary: {analysis_data['metadata_summary']}\n")

    if os.path.exists(ANALYSIS_JSON_FILE):
        with open(ANALYSIS_JSON_FILE, "r") as json_file:
            historical_data = json.load(json_file)
    else:
        historical_data = {}

    historical_data.setdefault(current_date, []).append({
        "timestamp": datetime.now().isoformat(),
        "analysis": analysis_data
    })

    with open(ANALYSIS_JSON_FILE, "w") as json_file:
        json.dump(historical_data, json_file, indent=2)

topics = [
    'Hot Videos', 'Apparel & Accessories', 'Baby, Kids & Maternity', 'Beauty & Personal Care', 'Business Services',
    'Education', 'Financial Services', 'Food & Beverage', 'Games', 'Health', 'Home Improvement',
    'Household Products', 'Life Services', 'News & Entertainment', 'Pets', 'Sports & Outdoor',
    'Tech & Electronics', 'Travel', 'Vehicle & Transportation'
]

def initiate_topic_scraping(topic_index):
    """Starts scraping TikTok videos for a given topic index."""
    request_url = "http://localhost:8000/scrape-and-download/"
    request_payload = {
        "search_type": "topic",
        "search_query": str(topic_index),
        "max_videos": 6
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(request_url, headers=headers, json=request_payload)
        response_data = response.json()
        if "id" in response_data:
            monitor_scraping_status(response_data["id"], topic_index)
        else:
            print("Error: No scrape ID returned.")
    except requests.RequestException as err:
        print(f"Scraping request failed: {err}")

def initiate_hashtag_scraping(topic_index, hashtag):
    """Starts scraping TikTok videos for a given hashtag."""
    print(f"Initiating scraping for hashtag: {hashtag}")
    request_url = "http://localhost:8000/scrape-and-download/"
    request_payload = {
        "search_type": "hashtag",
        "search_query": hashtag,
        "max_videos": 5
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(request_url, headers=headers, json=request_payload)
        response_data = response.json()
        if "id" in response_data:
            return monitor_video_scraping(response_data["id"], topic_index, hashtag)
        else:
            print("Error: No scrape ID returned.")
    except requests.RequestException as err:
        print(f"Hashtag scraping request failed: {err}")

def monitor_video_scraping(scrape_id, topic_index, hashtag):
    """Monitors the status of a hashtag-based video scraping job."""
    status_url = f"http://localhost:8000/get-status/?id={scrape_id}"

    while True:
        time.sleep(5)
        try:
            response = requests.get(status_url)
            status_data = response.json()
            if status_data.get("status") == "completed":
                print("Scraping completed for hashtag:", hashtag)
                for video_info in status_data.get("videos", []):
                    video_path = f"/home/virt/Desktop/iZYUoIz_tiktok_scraper/IzYOuIz_tiktok_scraper{video_info['video']}"
                    metadata = {k: v for k, v in video_info.items() if k not in ["video", "userid", "videotiktok"]}
                    metadata.update({"tag": hashtag, "topic": topics[topic_index]})
                    analyze_tiktok_video(video_path, metadata)
                return status_data
        except requests.RequestException as err:
            print(f"Error checking video scraping status: {err}")

def monitor_scraping_status(scrape_id, topic_index):
    """Monitors the status of a topic-based scraping job."""
    status_url = f"http://localhost:8000/get-status/?id={scrape_id}"

    while True:
        time.sleep(5)
        try:
            response = requests.get(status_url)
            status_data = response.json()
            if status_data.get("status") == "completed":
                for hashtag in status_data.get("hashtags", []):
                    initiate_hashtag_scraping(topic_index, hashtag)
                break
        except requests.RequestException as err:
            print(f"Error checking scraping status: {err}")

if __name__ == "__main__":
    initiate_topic_scraping(4)
