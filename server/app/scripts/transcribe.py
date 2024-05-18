import json
import argparse
from pathlib import Path
from typing import List, Dict
from openai import OpenAI
from dotenv import dotenv_values

# Global variables
RAW_PATH = Path(__file__).parent.parent.joinpath('data', 'audio', 'raw')
SEGMENTED_PATH = Path(__file__).parent.parent.joinpath('data', 'audio', 'segmented')
VERBOSE_JSON_PATH = Path(__file__).parent.parent.joinpath('data', 'transcript', 'verbose_json')
TEXT_PATH = Path(__file__).parent.parent.joinpath('data', 'transcript', 'text')
OPENAI_API_KEY = dotenv_values(Path(__file__).parent.parent.joinpath('.env'))['OPENAI_API_KEY']

# Chek if paths exist
if not VERBOSE_JSON_PATH.exists():
    VERBOSE_JSON_PATH.mkdir(parents=True)
if not TEXT_PATH.exists():
    TEXT_PATH.mkdir(parents=True)

def main(
    file_name: str,
    prompt: str,
):
    """
    
    """
    
    # Check if target split audio files exist
    target_folder = RAW_PATH.joinpath(file_name)
    target_segmented_path = SEGMENTED_PATH.joinpath(target_folder.stem)
    
    assert target_segmented_path.exists(), f"{target_segmented_path} does not exist. You should run `split_audio.py` first."
    
    target_verbose_json_path = VERBOSE_JSON_PATH.joinpath(target_segmented_path.stem)
    if not target_verbose_json_path.exists():
        target_verbose_json_path.mkdir()
        print(f"{target_verbose_json_path} has been created.")
        
    target_text_path = TEXT_PATH.joinpath(target_segmented_path.stem)
    if not target_text_path.exists():
        target_text_path.mkdir()
        print(f"{target_text_path} has been created.")
    
    # Transcribe audio files
    transcribe_audio(target_segmented_path, prompt)
    

def transcribe_audio(
    target_segmented_path: Path,
    prompt: str,
):
    """
    
    :params:
        - target_segmented_path: A path contains target split audio files.
        - prompt
    """
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    print("Transcription starts...")
    idx = 0
    audio_files = list(target_segmented_path.iterdir())
    audio_files.sort()
    for audio_file in audio_files:
        
        # Consumes only mp3 files
        if audio_file.suffix == '.mp3':
            print(f"index: {idx}, Load an audio file... {audio_file}")
            audio_input = open(audio_file, 'rb')
            
            if prompt:
                print(f"index: {idx}, Transcribing...")
                transcription = client.audio.transcriptions.create(
                    file=audio_input,
                    language='en',
                    model='whisper-1',
                    response_format='verbose_json',
                    timestamp_granularities=['segment'],
                    prompt=prompt,
                )
            else:
                print(f"index: {idx}, Transcribing...")
                transcription = client.audio.transcriptions.create(
                    file=audio_input,
                    language='en',
                    model='whisper-1',
                    response_format='verbose_json',
                    timestamp_granularities=['segment'],
                )

            if prompt:
                save_name = f"{audio_file.stem.replace('.mp3', '')}_prompt.json"
            else:
                save_name = f"{audio_file.stem.replace('.mp3', '')}.json"

            print(f"index: {idx}, Save a verbose_json file... {VERBOSE_JSON_PATH.joinpath(audio_file.parent.stem.replace('.mp3', ''), save_name)}")
            with open(VERBOSE_JSON_PATH.joinpath(audio_file.parent.stem.replace('.mp3', ''), save_name), 'w') as f:
                json.dump(transcription.segments, f)
                
            extract_text(idx, audio_file, prompt, transcription.segments)
            
        idx += 1

def extract_text(
    idx: int,
    audio_file: Path,
    prompt: str,
    verbose_json: List[Dict],
):
    """
    
    :params:
        - audio_file  : An auido file path.
        - prompt      : A prompt file path.
        - verbose_json: A list of dictionaries containing all transcription info.
    """
    
    if prompt:
        save_name = f"{audio_file.stem.replace('.mp3', '')}_prompt.txt"
    else:
        save_name = f"{audio_file.stem.replace('.mp3', '')}.txt"
    
    print(f"index: {idx}, Save a extracted text file... {TEXT_PATH.joinpath(audio_file.parent.stem, save_name)}")
    with open(TEXT_PATH.joinpath(audio_file.parent.stem, save_name), 'w') as f:
        f.write(''.join(d['text'] for d in verbose_json))


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file_name', type=str)
    parser.add_argument('-p', '--prompt', type=str, default='')
    
    args = parser.parse_args()
    
    main(
        args.file_name,
        args.prompt,
    )