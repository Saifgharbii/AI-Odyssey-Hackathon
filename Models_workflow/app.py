from image_gen import Text_Image2ImageGen
from video_gen import VideoGen
from speech_recognition import Speech2Text

from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import json
from PIL import Image
import io
import torchaudio

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  


@app.route('/generate_video', methods=['POST'])
def generate_video_route():
    print("Request received")
    if 'image' not in request.files:
        return {"error": "Missing image"}, 400
    
    image_file = request.files['image']
    data = request.get_json()
    if not data or 'prompt' not in data:
        return {"error": "Missing prompt"}, 400
    
    prompt = data['prompt']
    
    # Convert the image file to a PIL Image
    image = Image.open(io.BytesIO(image_file.read())).convert("RGB")
    
    # Generate the video directly in memory
    video_stream = VideoGen.generate_video(prompt, image)
    
    # Send the video file as a response without saving it locally
    return Response(video_stream.getvalue(), mimetype='video/mp4')

@app.route('/generate_image', methods=['POST'])
def generate_image_route():
    print("Request received")
    data = request.get_json()
    print(data)
    if 'image' not in request.files:
        image = None
    else:
        image_file = request.files['image']
        image = Image.open(io.BytesIO(image_file.read())).convert("RGB")
        output_image = Text_Image2ImageGen.generate_image(data['prompt'], image)
    
    # Save the output image to a BytesIO object
    img_io = io.BytesIO()
    output_image.save(img_io, 'JPEG')
    img_io.seek(0)
    
    # Send the image file as a response
    return send_file(img_io, mimetype='image/jpeg')
    
@app.route('/recognize_speech', methods=['POST'])
def recognize_speech_route():
    if 'audio' not in request.files:
        return {"error": "Missing audio file"}, 400
    
    audio_file = request.files['audio']  # Get the uploaded audio file
    audio_bytes = audio_file.read()  # Read audio content as bytes
    
    audio_stream = io.BytesIO(audio_bytes)

    # Load into torchaudio (directly from the stream)
    waveform, sample_rate = torchaudio.load(audio_stream)
    
    user_text = Speech2Text.speech_to_text(waveform, sample_rate)
    return jsonify({
        "message": "Audio received successfully",
        "user_text": user_text,
    })  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
