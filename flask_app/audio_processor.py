import yt_dlp
import os
from spleeter.separator import Separator
from spleeter.utils.logging import logger

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
        print("Please make sure the file name is correct and it's in the same directory.")
        return

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
        print(f"  - Vocals:     vocals.wav")
        print(f"  - Instrumental: accompaniment.wav")
        print("-------------------------------------------")

    except Exception as e:
        print(f"An error occurred during the separation process: {e}")


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