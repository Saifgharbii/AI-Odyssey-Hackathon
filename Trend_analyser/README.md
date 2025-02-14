# TikTok Video Analysis Pipeline

This project analyzes TikTok videos using the **Gemini API** to extract viral elements, provide recommendations, and summarize metadata. It processes scraped videos, downscales them for efficiency, and organizes the analysis results in both text and JSON formats.

---

## Features

- **Video Preprocessing**: Downscales videos to 10 FPS for faster processing.
- **Gemini Integration**: Analyzes videos and metadata to extract viral elements and recommendations.
- **Daily Analysis**: Saves results in a daily text file and a structured JSON file.
- **Metadata Integration**: Combines video analysis with scraped metadata (likes, comments, captions, etc.).
- **Easy Retrieval**: Organizes analysis data by day for quick access.

---

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`
- FFmpeg (for video processing)
- Gemini API key (stored in `.env`)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tiktok-analysis.git
   cd tiktok-analysis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your Gemini API key to a `.env` file:
   ```plaintext
   GEMINI_API_KEY=your_api_key_here
   ```

4. Install FFmpeg:
   - **Linux**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html).

---

## Usage

1. Place your scraped TikTok videos in the project directory.
2. Run the analysis script:
   ```bash
   python analyze_video.py
   ```
3. Results will be saved in:
   - **Text File**: `daily_analysis.txt`
   - **JSON File**: `analysis_data.json`

---

## Example

### Input:
- Video: `tiktok_baamitheultima_7468229111371156742.mp4`
- Metadata:
  ```json
  {
    "likes": 15000,
    "comments": 1200,
    "shares": 800,
    "caption": "This is how you make the perfect coffee! ☕️ #CoffeeLovers",
    "hashtags": ["#CoffeeLovers", "#BaristaLife", "#TikTokFood"]
  }
  ```

### Output:
- **Text File**:
  ```
  === Analysis on 2023-10-15 14:30:45 ===
  Viral Elements: The video uses quick cuts and engaging visuals...
  Recommendations: Add more close-up shots of the coffee-making process...
  Metadata Summary: The video received 15,000 likes, 1,200 comments, and 800 shares...
  ```

- **JSON File**:
  ```json
  {
    "2023-10-15": [
      {
        "timestamp": "2023-10-15T14:30:45",
        "analysis": {
          "viral_elements": "The video uses quick cuts and engaging visuals...",
          "recommendations": "Add more close-up shots of the coffee-making process...",
          "metadata_summary": "The video received 15,000 likes, 1,200 comments, and 800 shares..."
        }
      }
    ]
  }
  ```

---


This `README.md` provides a clear and concise overview of the project, making it easy for users to understand and use the tool.