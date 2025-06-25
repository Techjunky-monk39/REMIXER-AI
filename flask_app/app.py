# Deployment trigger: minor comment update for Cloud Build
# Date: 2025-06-22
# This comment is used to trigger a new deployment via GitHub push.

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import logging
from .audio_separator import separate_audio
from flask_app.yt_audio_downloader import download_youtube_audio

app = Flask(__name__)
CORS(app)  # Allow requests from your frontend

# Set up logging
logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    # Call the audio separation function
    output_dir = os.path.join(OUTPUT_FOLDER, os.path.splitext(file.filename)[0])
    os.makedirs(output_dir, exist_ok=True)
    separate_audio(filepath, output_dir)
    # Optionally, list the output files for download
    stems = os.listdir(output_dir)
    stem_urls = [
        f"/download/{os.path.splitext(file.filename)[0]}/{stem}"
        for stem in stems
    ]
    return jsonify({
        'message': 'File uploaded and split!',
        'stems': stem_urls
    })

@app.route('/download/<stem_folder>/<filename>')
def download_stem(stem_folder, filename):
    dir_path = os.path.join(OUTPUT_FOLDER, stem_folder)
    return send_from_directory(dir_path, filename, as_attachment=True)

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
        downloaded_audio_filepath = download_youtube_audio(url, output_path=UPLOAD_FOLDER)
        if downloaded_audio_filepath:
            app.logger.info(f"Audio downloaded: {downloaded_audio_filepath}")

            original_filename = os.path.basename(downloaded_audio_filepath)
            filename_without_ext = os.path.splitext(original_filename)[0]
            separation_output_dir = os.path.join(UPLOAD_FOLDER, filename_without_ext)
            os.makedirs(separation_output_dir, exist_ok=True)

            vocals_path, accompaniment_path = separate_audio(downloaded_audio_filepath, separation_output_dir)

            if vocals_path and accompaniment_path:
                return jsonify({
                    'message': 'Audio downloaded and processed successfully!',
                    'original_filename': original_filename,
                    'vocals_path': os.path.relpath(vocals_path, UPLOAD_FOLDER).replace('\\', '/'),
                    'accompaniment_path': os.path.relpath(accompaniment_path, UPLOAD_FOLDER).replace('\\', '/')
                })
            else:
                app.logger.error(f"Failed to separate audio for {downloaded_audio_filepath}")
                return jsonify({'error': 'Failed to process audio after download'}), 500
        else:
            app.logger.error(f"Failed to download audio from URL: {url}")
            return jsonify({'error': 'Failed to download audio.'}), 500
    except Exception as e:
        app.logger.error(f"Error processing URL {url}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download_separated/<path:filepath>')
def download_separated_file(filepath):
    # Construct the full path to the file
    # The `filepath` received from the URL will be e.g., "original_filename_without_ext/vocals.wav"
    # We need to join it with our actual UPLOAD_FOLDER
    # UPLOAD_FOLDER is 'uploads'
    # So, full_path will be 'uploads/original_filename_without_ext/vocals.wav'
    full_path = os.path.join(UPLOAD_FOLDER, filepath)
    app.logger.info(f"Attempting to send file from: {full_path}")

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        app.logger.error(f"File not found or is not a file: {full_path}")
        return jsonify({'error': 'File not found'}), 404

    try:
        return send_file(full_path, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error sending file {full_path}: {str(e)}")
        return jsonify({'error': 'Could not send file'}), 500

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
