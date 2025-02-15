from flask import Flask, request, jsonify, Response
import requests
from moviepy import VideoFileClip, AudioFileClip
import io
import threading
from Gemenai_workflow.Gemanai_workflow import process_user_input

app = Flask(__name__)

# Configuration
AUDIO_SERVER = "http://localhost:5001/generate_audio"
VIDEO_SERVER = "http://localhost:5002/generate_video"
IMAGE_SERVER = "http://localhost:5002/generate_image"
SPEECH_SERVER = "http://localhost:5002/recognize_speech"

def mix_audio_video(video_bytes, audio_bytes):
    """
    Mixes audio and video into a single video file.

    Args:
        video_bytes (bytes): The video file as bytes.
        audio_bytes (bytes): The audio file as bytes.

    Returns:
        bytes: The mixed video file as bytes.
    """
    # Save to temporary files
    with open("temp_video.mp4", "wb") as f:
        f.write(video_bytes)
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)
    
    # Mix using moviepy
    video = VideoFileClip("temp_video.mp4")
    audio = AudioFileClip("temp_audio.wav")
    final_video = video.set_audio(audio)
    
    # Export to bytes
    output = io.BytesIO()
    final_video.write_videofile(output, codec="libx264", audio_codec="aac")
    return output.getvalue()

@app.route('/generate_content', methods=['POST'])
def handle_content_creation():
    """
    Handles the content creation workflow.
    """
    user_input = ""
    print("those are request : {request}")
    # Handle audio/text input
    if 'audio' in request.files:
        audio_file = request.files['audio']
        # Convert speech to text
        response = requests.post(SPEECH_SERVER, files={'audio': audio_file})
        user_input = response.json().get('user_text', '')
    else:
        user_input = request.json.get('text')
        if not user_input:
            return jsonify({"error": "Either 'audio' or 'text' must be provided"}), 400
    print(user_input)
    # Process user input
    content_specs = process_user_input(user_input)
    print(f"those are the content from llm {content_specs['image_prompt']}")

    # Generate image
    image_response = requests.post(IMAGE_SERVER, json={
        "prompt": content_specs['image_prompt']
    })
    print(f"this is image response : {image_response}")

    # Generate video
    generate_video(content_specs, image_response.content)

    # Then generate audio
    generate_audio(content_specs)

    # Mix audio and video
    mixed_video = mix_audio_video(video_bytes=video_result, audio_bytes=audio_result)

    # Return final video
    return Response(mixed_video, mimetype='video/mp4')

def generate_video(specs, image_bytes):
    """
    Generates a video using the video server.

    Args:
        specs (dict): Content specifications.
        image_bytes (bytes): The image file as bytes.

    Returns:
        bytes: The generated video as bytes.
    """
    global video_result
    files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
    response = requests.post(VIDEO_SERVER, 
        files=files,
        data={'prompt': specs['video_prompt']}
    )
    video_result = response.content

def generate_audio(specs):
    """
    Generates audio using the audio server.

    Args:
        specs (dict): Content specifications.

    Returns:
        bytes: The generated audio as bytes.
    """
    global audio_result
    response = requests.post(AUDIO_SERVER, json={
        "script": specs['script'],
        "audio_prompt": specs['audio_prompt']
    })
    audio_result = response.content

if __name__ == '__main__':
    app.run(port=5000, threaded=True)