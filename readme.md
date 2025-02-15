# AI Content Generator for Business

## Project Overview
This AI-powered content generator is designed to help businesses create engaging digital content efficiently. By leveraging multiple AI models, it extracts trending TikTok content and processes it to generate text, images, and videos. The project is part of our submission for the **AI-Odyssey-Hackathon**.

## Features
- **Content Scraping**: Uses Giminia to extract trending content from TikTok.
- **Speech-to-Text**: Converts spoken words into text using Seamless-M4T.
- **Text-to-Image**: Generates images from text prompts using Stable Diffusion.
- **Image-to-Video**: Creates videos from images using CogVideoX.
- **Text-to-Speech**: Converts text into speech using Parler-TTS.

## Architecture
The project operates on three main servers:
1. **Main Server (`main_server`)**: Handles primary application logic and API requests.
2. **Models Workflow (`models_workflow`)**: Manages AI model interactions.
3. **Speech Generation (`speech_gen`)**: Generates speech from text.

These servers communicate over a shared Docker network to ensure smooth integration.

## Installation & Running the Project
### Prerequisites
- Docker installed on your system.
- Python 3.x (for local development and debugging).

### Steps to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/ai-content-generator.git
   cd ai-content-generator
   ```
2. Ensure Docker is installed and running.
3. Start the application with:
   ```bash
   docker-compose up --build
   ```
4. Access the services through the following ports:
   - **Main Server**: `http://localhost:8000`
   - **Models Workflow**: `http://localhost:8001`
   - **Speech Generation**: `http://localhost:8002`

## How the Script Works
The script is a Flask-based API that handles content generation requests. Below is a breakdown of its core functionalities:

### API Endpoints
#### `/generate_content` (POST)
This endpoint processes user input, generates content, and returns a final video.

#### Steps:
1. **Receive Input**: Accepts user input in the form of text or audio.
   - If audio is provided, it is sent to the **Speech-to-Text server** to convert it into text.
   - If text is provided, it is processed directly.
2. **Process Input**: Uses `process_user_input()` from `Gemenai_workflow` to analyze the user’s intent and generate content specifications.
3. **Generate Image**: Calls the **Image Generation server** to create an image from the prompt.
4. **Generate Video**: Sends the generated image to the **Video Generation server**, along with a video prompt.
5. **Generate Audio**: Uses the **Text-to-Speech server** to generate an audio clip from the script.
6. **Mix Audio & Video**: Combines the generated audio and video using `moviepy` to create a final video output.
7. **Return Final Video**: Sends the processed video file back to the user as a response.

### Functions Explained
#### `mix_audio_video(video_bytes, audio_bytes)`
- Mixes the generated audio and video files into a single video file.
- Uses `moviepy` to overlay audio onto the video and exports the final video.

#### `generate_video(specs, image_bytes)`
- Sends an image and video prompt to the **Video Generation server** to create a video.

#### `generate_audio(specs)`
- Calls the **Audio Generation server** with the generated script to create an audio file.

## Future Enhancements
- Improve speech-to-text accuracy by integrating better models.
- Add more customization options for video editing.
- Enhance scalability by deploying services using Kubernetes.

## License
This project is licensed under the MIT License.

**Good luck to us in the AI-Odyssey-Hackathon!** 🚀

