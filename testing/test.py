from flask import Flask, request, jsonify
import time
import base64
import os

app = Flask(__name__)

# Configure storage paths
STORAGE_PATH = 'storage'
IMAGE_PATH = os.path.join(STORAGE_PATH, 'sample_image.jpg')
VIDEO_PATH = os.path.join(STORAGE_PATH, 'sample_video.mp4')

@app.route('/process', methods=['POST'])
def process_request():
    # Get prompt from request
    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    # Simulate processing time
    time.sleep(8)
    
    try:
        # Predefined response text
        response_text = f"Here's your response for: {prompt}\nThis is a predefined response text that you can customize."
        
        # Read and encode image
        with open(IMAGE_PATH, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
        
        # Read and encode video
        with open(VIDEO_PATH, 'rb') as video_file:
            video_data = base64.b64encode(video_file.read()).decode()
        
        return jsonify({
            'text': response_text,
            'image_data': f'data:image/jpeg;base64,{img_data}',
            'video_data': f'data:video/mp4;base64,{video_data}'
        })
        
    except FileNotFoundError as e:
        return jsonify({'error': 'Media files not found. Please check storage directory.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response

if __name__ == '_main_':
    # Create storage directory if it doesn't exist
    if not os.path.exists(STORAGE_PATH):
        os.makedirs(STORAGE_PATH)
    app.run(debug=True, port=5004)