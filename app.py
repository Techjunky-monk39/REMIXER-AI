from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allow requests from your frontend

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return {'status': 'Backend running!'}

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    # TODO: Call your audio processing here
    return jsonify({'message': 'File uploaded', 'filename': file.filename})

@app.route('/process', methods=['POST'])
def process_audio():
    data = request.json
    # TODO: Call your audio_processor.py or other logic here
    return jsonify({'message': 'Processing started', 'params': data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
