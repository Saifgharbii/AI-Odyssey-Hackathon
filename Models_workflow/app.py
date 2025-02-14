from . import SpeechGen
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  

@app.route('/generate_audio', methods=['POST'])
def generate_audio_route():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Generate speech
        audio_file = SpeechGen.generate_speech(prompt=data["script"],description=data["audio_prompt"])

        # Send the audio file in the response
        return send_file(audio_file, mimetype="audio/wav", as_attachment=True, download_name="generated_audio.wav")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
