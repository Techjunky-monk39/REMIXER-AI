# yt_audio_downloader.py
"""
Download audio from a YouTube URL and save it as a file.
"""
import os
import yt_dlp

def download_youtube_audio(url, output_path='uploads'):
    """
    Downloads audio from a YouTube URL and saves it as an mp3 file in the output_path.
    Returns the path to the downloaded file, or None if failed.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            mp3_filename = os.path.splitext(filename)[0] + '.mp3'
            if os.path.exists(mp3_filename):
                return mp3_filename
            else:
                return None
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None
