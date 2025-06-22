a# Deployment trigger: minor comment update for Cloud Build
# Date: 2025-06-22
# This comment is used to trigger a new deployment via GitHub push.

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import logging
from flask_app.yt_audio_downloader import download_youtube_audio

app = Flask(__name__)
CORS(app)  # Allow requests from your frontend

# Set up logging
logging.basicConfig(level=logging.INFO)

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

@app.route('/process_url', methods=['POST'])
def process_url():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    try:
        filename = download_youtube_audio(url, output_path=UPLOAD_FOLDER)
        if filename:
            return jsonify({'message': f'Audio downloaded successfully!', 'filename': filename})
        else:
            return jsonify({'error': 'Failed to download audio.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint for Cloud Run
@app.route('/healthz')
def healthz():
    return jsonify({'status': 'ok'}), 200

# Robust error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
