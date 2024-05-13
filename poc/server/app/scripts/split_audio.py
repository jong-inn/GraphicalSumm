import argparse
import shutil
from pathlib import Path
from pydub import AudioSegment

AUDIO_PATH = Path(__file__).parent.parent.joinpath('data', 'audio')


def main(
    file_name: str,
):
    """
    
    """
    
    file_path = AUDIO_PATH.joinpath('raw', file_name)
    file_size = file_path.stat().st_size / (pow(10, 6))
    file_format = file_path.suffix.replace('.', '')
    
    print(f"""
    file path  : {file_path}
    file size  : {file_size} MB
    file format: {file_format}
""")

    # Prepare a sub-directory under segmented
    segmented_path = AUDIO_PATH.joinpath('segmented', file_path.stem)
    if segmented_path.exists():
        shutil.rmtree(segmented_path)
    segmented_path.mkdir()
    
    # Load the target audio file
    raw_audio = AudioSegment.from_file(str(file_path), format=file_format)
    
    if file_size > 25:
        # To decrease the size of a raw audio file, keep the length of each audio less than 22 minutes.
        print(f"Split the target audio file...")
        sliced_minutes = 22 * 60 * 1000
        
        for i, chunk in enumerate(raw_audio[::sliced_minutes]):
            # Output audio files will be in a mp3 format
            with open(segmented_path.joinpath(f'{file_path.stem}_{i}.mp3'), 'wb') as f:
                chunk.export(f, format='mp3')
                print(f"data/audio/segmented/{file_path.stem}/{file_path.stem}_{i}.mp3 has been created.")
    else:
        print(f"Size of the file is less than 25 MB. The original file has been copied to the segemented folder.")
        with open(segmented_path.joinpath(f'{file_path.stem}_0.mp3'), 'wb') as f:
            raw_audio.export(f, format='mp3')
            

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file_name', type=str)
    
    args = parser.parse_args()
    
    main(
        args.file_name,
    )