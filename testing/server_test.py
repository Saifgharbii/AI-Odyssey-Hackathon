# File: test_server.py (Flask server on port 5003)
from flask import Flask, request, jsonify, render_template_string, Response
import requests

app = Flask(__name__)
BASE_SERVER = "http://localhost:5000"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Content Creator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .container { max-width: 800px; margin-top: 2rem; }
        #progress-container { margin-top: 2rem; display: none; }
        .progress-step { margin: 0.5rem 0; padding: 1rem; border-radius: 5px; }
        .record-btn { transition: all 0.3s; }
        .pulsing { animation: pulse 1.5s infinite; }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Create TikTok Content</h1>
        
        <div class="card mb-4">
            <div class="card-body">
                <div class="mb-3">
                    <label class="form-label">Text Input</label>
                    <textarea class="form-control" id="text-input" rows="3"></textarea>
                </div>
                <button class="btn btn-primary" onclick="submitText()">Submit Text</button>
                
                <hr>
                
                <div class="text-center">
                    <button id="record-btn" class="btn btn-danger record-btn" 
                            onmousedown="startRecording()" onmouseup="stopRecording()">
                        🎤 Hold to Record
                    </button>
                    <audio id="audio-preview" class="mt-2" controls></audio>
                </div>
            </div>
        </div>

        <div id="progress-container" class="card">
            <div class="card-body">
                <h5 class="card-title">Progress</h5>
                <div id="progress-steps"></div>
            </div>
        </div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        
        async function startRecording() {
            document.getElementById('record-btn').classList.add('pulsing');
            
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.start();
            } catch (err) {
                showError('Microphone access denied!');
            }
        }

        async function stopRecording() {
            document.getElementById('record-btn').classList.remove('pulsing');
            
            if (mediaRecorder) {
                mediaRecorder.stop();
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    audioChunks = [];
                    
                    // Preview audio
                    const audioUrl = URL.createObjectURL(audioBlob);
                    document.getElementById('audio-preview').src = audioUrl;
                    
                    // Submit audio
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'recording.wav');
                    
                    try {
                        const response = await fetch('/generate_content', {
                            method: 'POST',
                            body: formData
                        });
                        
                        handleResponse(await response.json());
                    } catch (error) {
                        showError('Submission failed!');
                    }
                };
            }
        }

        async function submitText() {
            const text = document.getElementById('text-input').value;
            if (!text) return showError('Please enter some text!');
            
            showProgress('Starting processing...');
            
            try {
                const response = await fetch('/generate_content', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                
                handleResponse(await response.json());
            } catch (error) {
                showError('Submission failed!');
            }
        }

        function handleResponse(response) {
            if (response.url) {
                addProgressStep('✅ Processing complete!', 'success');
                const link = document.createElement('a');
                link.href = response.url;
                link.download = 'final_video.mp4';
                link.className = 'btn btn-success mt-2';
                link.textContent = 'Download Video';
                document.getElementById('progress-steps').appendChild(link);
            }
        }

        function showProgress(message) {
            document.getElementById('progress-container').style.display = 'block';
            addProgressStep(message);
        }

        function addProgressStep(text, type='info') {
            const step = document.createElement('div');
            step.className = `progress-step bg-${type} bg-opacity-25 text-${type}`;
            step.textContent = `➤ ${new Date().toLocaleTimeString()}: ${text}`;
            document.getElementById('progress-steps').appendChild(step);
        }

        function showError(message) {
            addProgressStep(`❌ ${message}`, 'danger');
        }

        // Listen for server-sent events
        const eventSource = new EventSource('/progress');
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            addProgressStep(data.message, data.status);
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate_content', methods=['POST'])
def proxy_content():
    # Forward request to base server
    files = {'audio': request.files.get('audio')} if 'audio' in request.files else None
    data = request.form if files else request.json
    print(data)
    response = requests.post(
        f"{BASE_SERVER}/generate_content",
        files=files,
        json=data
    )
    print(f"this is response : {response}")
    
    return jsonify(response.json()), response.status_code

@app.route('/progress')
def progress_updates():
    # This would need proper server-sent events implementation
    # Simplified for demonstration
    def generate():
        yield "data: {}\n\n"
        
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(port=5003, debug=True)