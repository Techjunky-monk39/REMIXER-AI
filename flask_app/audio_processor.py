import yt_dlp
import os
from spleeter.separator import Separator
from spleeter.utils.logging import logger
import librosa
import soundfile as sf
from pydub import AudioSegment, effects
import numpy as np

def download_youtube_audio(url, output_path='.'):
    """
    Downloads the audio from a YouTube video as an MP3 file.

    Args:
        url (str): The URL of the YouTube video.
        output_path (str): The directory where the audio file will be saved.
                            Defaults to the current directory.

    Returns:
        str: The filename of the downloaded audio, or None if it fails.
    """
    try:
        # Configuration for yt-dlp to get the best audio and convert to mp3.
        # The 'outtmpl' setting determines the output filename.
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # This template creates a filename like "Video Title.mp3"
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'noplaylist': True,  # Ensures only the single video is downloaded
        }

        print(f"Starting download for: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            # After download, the final filename is created by yt-dlp
            # We can construct it from the info dictionary
            filename = ydl.prepare_filename(info_dict)
            # The extension is changed by the postprocessor, so we adjust it
            base, _ = os.path.splitext(filename)
            final_filename = base + '.mp3'

        print(f"\nSuccessfully downloaded audio.")
        print(f"File saved as: {final_filename}")
        return final_filename

    except yt_dlp.utils.DownloadError as e:
        print(f"Error: Invalid YouTube URL or download failed. Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def separate_audio(audio_file_path, output_dir='output'):
    """
    Separates an audio file into vocal and accompaniment tracks using Spleeter.

    Args:
        audio_file_path (str): The path to the input audio file (e.g., "MySong.mp3").
        output_dir (str): The directory to save the separated files.
    """
    # Check if the audio file exists before processing
    if not os.path.exists(audio_file_path):
        print(f"Error: Cannot find the file '{audio_file_path}'.")
        # Return None or raise an exception to indicate failure
        return None, None

    try:
        # Spleeter can be very verbose; this reduces the log noise.
        logger.setLevel('ERROR')

        # Initialize the separator. It will download models on the first run.
        # 'spleeter:2stems' separates audio into 'vocals' and 'accompaniment'.
        separator = Separator('spleeter:2stems')

        print(f"Processing '{audio_file_path}'... This may take a moment.")

        # The separation process creates a new folder within the output_dir.
        # The folder will be named after the input file (without extension).
        separator.separate_to_file(audio_file_path, output_dir)

        # Determine the name of the folder where results are saved
        output_folder_name = os.path.splitext(os.path.basename(audio_file_path))[0]
        full_output_path = os.path.join(output_dir, output_folder_name)

        print("\n-------------------------------------------")
        print("Separation Complete!")
        print(f"Files saved in: '{full_output_path}'")
        vocals_path = os.path.join(full_output_path, "vocals.wav")
        accompaniment_path = os.path.join(full_output_path, "accompaniment.wav")
        print(f"  - Vocals:     {vocals_path}")
        print(f"  - Instrumental: {accompaniment_path}")
        print("-------------------------------------------")
        return vocals_path, accompaniment_path

    except Exception as e:
        print(f"An error occurred during the separation process: {e}")
        return None, None


def change_tempo(input_path, output_path, tempo_factor):
    """
    Changes the tempo of an audio file.
    Args:
        input_path (str): Path to input audio file.
        output_path (str): Path to save the tempo-changed audio.
        tempo_factor (float): >1.0 speeds up, <1.0 slows down.
    """
    y, sr = librosa.load(input_path, sr=None)
    y_stretch = librosa.effects.time_stretch(y, tempo_factor)
    sf.write(output_path, y_stretch, sr)

def change_pitch(input_path, output_path, n_steps):
    """
    Changes the pitch of an audio file.
    Args:
        input_path (str): Path to input audio file.
        output_path (str): Path to save the pitch-shifted audio.
        n_steps (float): Number of semitones to shift (positive or negative).
    """
    y, sr = librosa.load(input_path, sr=None)
    y_shift = librosa.effects.pitch_shift(y, sr, n_steps)
    sf.write(output_path, y_shift, sr)

def add_reverb(input_path, output_path, reverb_amount=0.5):
    """
    Adds a simple reverb effect to an audio file.
    Args:
        input_path (str): Path to input audio file.
        output_path (str): Path to save the audio with reverb.
        reverb_amount (float): 0.0 (none) to 1.0 (max)
    """
    audio = AudioSegment.from_file(input_path)
    # Simple reverb: overlay a delayed, quieter version of the audio
    delay_ms = 80
    decay = reverb_amount
    reverb = audio - (10 * (1 - decay))
    reverb = reverb.fade(to_gain=-120, start=0, duration=delay_ms)
    combined = audio.overlay(reverb, position=delay_ms)
    combined.export(output_path, format="wav")

def mix_stems(vocals_path, accompaniment_path, output_path, vocals_gain=0, acc_gain=0):
    """
    Mixes vocals and accompaniment stems into a single track.
    Args:
        vocals_path (str): Path to vocals stem.
        accompaniment_path (str): Path to accompaniment stem.
        output_path (str): Path to save the mixed audio.
        vocals_gain (float): dB gain for vocals.
        acc_gain (float): dB gain for accompaniment.
    """
    vocals = AudioSegment.from_file(vocals_path)
    acc = AudioSegment.from_file(accompaniment_path)
    vocals = vocals + vocals_gain
    acc = acc + acc_gain
    remix = acc.overlay(vocals)
    remix.export(output_path, format="wav")

def process_remix(vocals_path, accompaniment_path, output_dir, tempo=1.0, pitch=0, reverb=0.0):
    """
    Applies tempo, pitch, and reverb to stems and mixes them.
    Returns the path to the remixed file.
    """
    # Temp files for processing
    vocals_tmp = os.path.join(output_dir, "vocals_tmp.wav")
    acc_tmp = os.path.join(output_dir, "acc_tmp.wav")
    vocals_proc = vocals_path
    acc_proc = accompaniment_path
    # Tempo
    if tempo != 1.0:
        change_tempo(vocals_proc, vocals_tmp, tempo)
        change_tempo(acc_proc, acc_tmp, tempo)
        vocals_proc = vocals_tmp
        acc_proc = acc_tmp
    # Pitch
    if pitch != 0:
        change_pitch(vocals_proc, vocals_tmp, pitch)
        change_pitch(acc_proc, acc_tmp, pitch)
        vocals_proc = vocals_tmp
        acc_proc = acc_tmp
    # Reverb (only on vocals for demo)
    if reverb > 0.0:
        add_reverb(vocals_proc, vocals_tmp, reverb)
        vocals_proc = vocals_tmp
    # Mix
    remix_path = os.path.join(output_dir, "remix.wav")
    mix_stems(vocals_proc, acc_proc, remix_path)
    # Clean up temp files if needed
    for f in [vocals_tmp, acc_tmp]:
        if os.path.exists(f):
            os.remove(f)
    return remix_path


if __name__ == '__main__':
    # --- USAGE ---
    # 1. Paste the YouTube URL here
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with your desired video URL
    download_dir = "downloaded_audio"  # Directory to save downloaded audio
    separated_dir = "separated_tracks"  # Directory to save separated tracks

    # Create directories if they don't exist
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(separated_dir, exist_ok=True)

    # 2. Download the audio
    downloaded_audio_file = download_youtube_audio(video_url, download_dir)

    # 3. If the download was successful, separate the audio
    if downloaded_audio_file:
        separate_audio(downloaded_audio_file, separated_dir)
    else:
        print("Audio download failed.  Cannot proceed with separation.")