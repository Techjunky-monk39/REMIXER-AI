import yt_dlp
import os

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
            'noplaylist': True, # Ensures only the single video is downloaded
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

if __name__ == '__main__':
    # --- USAGE ---
    # 1. Paste the YouTube URL here
    video_url = "https://www.youtube.com/watch?v=ioOzsi9aHQQ&list=RDioOzsi9aHQQ&start_radio=1"
    
    # 2. Run the script
    download_youtube_audio(video_url)