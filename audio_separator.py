import os
from spleeter.separator import Separator
from spleeter.utils.logging import logger

def separate_audio(audio_file_path, output_dir='output'):
    """
    Separates an audio file into vocal and accompaniment tracks.

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
        print(f"  - Vocals:       vocals.wav")
        print(f"  - Instrumental: accompaniment.wav")
        print("-------------------------------------------")

    except Exception as e:
        print(f"An error occurred during the separation process: {e}")


if __name__ == '__main__':
    # --- USAGE ---
    # 1. Make sure 'youtube_audio_extractor.py' has been run successfully.
    # 2. Enter the exact filename of the downloaded MP3 file here.
    input_audio_file = "Rick Astley - Never Gonna Give You Up.mp3" # Replace with your audio file's name

    # 3. Run the script
    separate_audio(input_audio_file)
