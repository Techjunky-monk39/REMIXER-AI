# Deployment trigger: minor comment update for Cloud Build
# Date: 2025-06-22
# This comment is used to trigger a new deployment via GitHub push.

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import logging
from audio_separator import separate_audio
from yt_audio_downloader import download_youtube_audio  # <-- FIXED: removed flask_app. prefix
from audio_processor import process_remix

app = Flask(__name__)
CORS(app)  # Allow requests from your frontend

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)
logger = logging.getLogger("remixer-backend")

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
    logger.info("Received upload request")
    if 'file' not in request.files:
        logger.warning("No file part in request")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        logger.warning("No selected file")
        return jsonify({'error': 'No selected file'}), 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    logger.info(f"Saved uploaded file to {filepath}")
    # Call the audio separation function
    output_dir = os.path.join(OUTPUT_FOLDER, os.path.splitext(file.filename)[0])
    os.makedirs(output_dir, exist_ok=True)
    try:
        separate_audio(filepath, output_dir)
        logger.info(f"Audio separated for {filepath}")
    except Exception as e:
        logger.error(f"Audio separation failed: {e}")
        return jsonify({'error': f'Audio separation failed: {str(e)}'}), 500
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
    logger.info(f"Download request for {dir_path}/{filename}")
    try:
        return send_from_directory(dir_path, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return jsonify({'error': f'Could not download file: {str(e)}'}), 500

@app.route('/process', methods=['POST'])
def process_audio():
    data = request.json
    logger.info(f"Received remix process request: {data}")
    # Expecting: {"vocals_path": ..., "accompaniment_path": ..., "tempo": ..., "pitch": ..., "reverb": ...}
    vocals_path = data.get('vocals_path')
    accompaniment_path = data.get('accompaniment_path')
    tempo = float(data.get('tempo', 1.0))
    pitch = float(data.get('pitch', 0))
    reverb = float(data.get('reverb', 0.0))
    output_dir = OUTPUT_FOLDER

    if not vocals_path or not accompaniment_path:
        return jsonify({'error': 'Missing vocals or accompaniment path'}), 400

    # Convert relative to absolute paths if needed
    vocals_abs = vocals_path if os.path.isabs(vocals_path) else os.path.join(output_dir, vocals_path)
    acc_abs = accompaniment_path if os.path.isabs(accompaniment_path) else os.path.join(output_dir, accompaniment_path)
    remix_output_dir = os.path.dirname(vocals_abs)

    try:
        remix_path = process_remix(vocals_abs, acc_abs, remix_output_dir, tempo=tempo, pitch=pitch, reverb=reverb)
        if remix_path and os.path.exists(remix_path):
            remix_rel = os.path.relpath(remix_path, OUTPUT_FOLDER).replace('\\', '/')
            logger.info(f"Remix created at {remix_path}")
            return jsonify({'message': 'Remix created!', 'remix_url': f"/download/{remix_rel}"})
        else:
            logger.error("Remix failed: output file not found")
            return jsonify({'error': 'Remix failed'}), 500
    except Exception as e:
        logger.error(f"Remix error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/process_url', methods=['POST'])
def process_url():
    data = request.get_json()
    url = data.get('url')
    logger.info(f"Received process_url request: {url}")
    if not url:
        logger.warning("No URL provided in process_url request")
        return jsonify({'error': 'No URL provided'}), 400
    try:
        downloaded_audio_filepath = download_youtube_audio(url, output_path=UPLOAD_FOLDER)
        if downloaded_audio_filepath:
            logger.info(f"Audio downloaded: {downloaded_audio_filepath}")
            original_filename = os.path.basename(downloaded_audio_filepath)
            filename_without_ext = os.path.splitext(original_filename)[0]
            separation_output_dir = os.path.join(UPLOAD_FOLDER, filename_without_ext)
            os.makedirs(separation_output_dir, exist_ok=True)
            vocals_path, accompaniment_path = separate_audio(downloaded_audio_filepath, separation_output_dir)
            if vocals_path and accompaniment_path:
                logger.info(f"Audio separated for {downloaded_audio_filepath}")
                return jsonify({
                    'message': 'Audio downloaded and processed successfully!',
                    'original_filename': original_filename,
                    'vocals_path': os.path.relpath(vocals_path, UPLOAD_FOLDER).replace('\\', '/'),
                    'accompaniment_path': os.path.relpath(accompaniment_path, UPLOAD_FOLDER).replace('\\', '/')
                })
            else:
                logger.error(f"Failed to separate audio for {downloaded_audio_filepath}")
                return jsonify({'error': 'Failed to process audio after download'}), 500
        else:
            logger.error(f"Failed to download audio from URL: {url}")
            return jsonify({'error': 'Failed to download audio.'}), 500
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download_separated/<path:filepath>')
def download_separated_file(filepath):
    full_path = os.path.join(UPLOAD_FOLDER, filepath)
    logger.info(f"Attempting to send file from: {full_path}")
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        logger.error(f"File not found or is not a file: {full_path}")
        return jsonify({'error': 'File not found'}), 404
    try:
        return send_file(full_path, as_attachment=True)
    except Exception as e:
        logger.error(f"Error sending file {full_path}: {str(e)}")
        return jsonify({'error': 'Could not send file'}), 500

# Health check endpoint for Cloud Run
@app.route('/healthz')
def healthz():
    return jsonify({'status': 'ok'}), 200

# Robust error handlers
@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({'error': 'Not found', 'path': request.path}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500 Internal Server Error: {str(e)}")
    return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
