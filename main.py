from flask import Flask, request, jsonify
from flask_cors import CORS
from .Models_workflow.image_gen import Text2ImageGen
from .Models_workflow.speech_gen import SpeechGen
from .Models_workflow.video_gen import VideoGen
from .Models_workflow.speech_recognition import Speech2Text
import os
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes

BASE_SERVER_URL = "http://127.0.0.1:5000/upload"  # Change this to your base server URL

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Error handling for CORS preflight requests
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route("/")
def home():
    return jsonify({"message": "AI Model Server is running!"})


@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    audio_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(audio_path)

    text_output = Speech2Text.speech_to_text(audio_path=audio_path)

    # Send to base server
    response = requests.post(BASE_SERVER_URL, json={"text_output": text_output})

    return jsonify({"transcribed_text": text_output, "base_response": response.json()})


@app.route("/text-to-image", methods=["POST"])
def text_to_image():
    data = request.json
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    output_path = os.path.join(OUTPUT_FOLDER, "generated_image.png")
    Text2ImageGen.generate_image(prompt=prompt, output_path=output_path)

    # Send file to base server
    with open(output_path, "rb") as file:
        response = requests.post(BASE_SERVER_URL, files={"file": file})

    return jsonify({"message": "Image sent to base server", "base_response": response.json()})


@app.route("/text-to-speech", methods=["POST"])
def text_to_speech():
    data = request.json
    text = data.get("text")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    output_path = os.path.join(OUTPUT_FOLDER, "generated_speech.wav")
    SpeechGen.generate_speech(text, output_path=output_path)

    # Send file to base server
    with open(output_path, "rb") as file:
        response = requests.post(BASE_SERVER_URL, files={"file": file})

    return jsonify({"message": "Speech sent to base server", "base_response": response.json()})


@app.route("/text-to-video", methods=["POST"])
def text_to_video():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files["image"]
    image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
    image_file.save(image_path)

    data = request.form
    prompt = data.get("prompt", "Default video prompt")

    output_path = os.path.join(OUTPUT_FOLDER, "generated_video.mp4")
    VideoGen.generate_video(prompt=prompt, image_path=image_path)

    # Send file to base server
    with open(output_path, "rb") as file:
        response = requests.post(BASE_SERVER_URL, files={"file": file})

    return jsonify({"message": "Video sent to base server", "base_response": response.json()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
