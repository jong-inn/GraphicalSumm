import json
import time
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from openai import OpenAI
from dotenv import dotenv_values
from utils import MODELS_INFO, num_tokens_from_string, split_into_chunks, generate_output

# Global variables
CURRENT_DATE = datetime.now().strftime('%Y%m%d')
VERBOSE_JSON_PATH = Path(__file__).parent.parent.joinpath('data', 'transcript', 'verbose_json')
PROMPTS_PATH = Path(__file__).parent.parent.joinpath('prompts', 'summarize_prompts.json')
TEXT_PATH = Path(__file__).parent.parent.joinpath('data', 'transcript', 'text')
SUMMARY_PATH = Path(__file__).parent.parent.joinpath('data', 'summary')
OPENAI_API_KEY = dotenv_values(Path(__file__).parent.parent.parent.joinpath('.env'))['OPENAI_API_KEY']
ABSTRACTIVE_PROMPT_N_LIMIT = 5

if not SUMMARY_PATH.exists():
    SUMMARY_PATH.mkdir()
    print(f"{SUMMARY_PATH} has been created.")

def main(
    folder_name: str,
    model_name: str,
):  
    assert model_name in MODELS_INFO, f"{model_name} is not allowed.\nModel candidates are {', '.join(MODELS_INFO.keys())}."
    
    target_path = TEXT_PATH.joinpath(folder_name)
    assert target_path.exists(), f"{target_path} does not exist."
    
    # Check save paths
    save_paths = {'extractive': '', 'abstractive': '', 'reduced': ''}
    for summary_type in save_paths.keys():
        save_root = SUMMARY_PATH.joinpath(folder_name, summary_type)
        if save_root.exists():
            existing_dir_num = len([p for p in save_root.iterdir() if p.is_dir() and (CURRENT_DATE == p.stem[:8])])
            save_path = save_root.joinpath(f'{CURRENT_DATE}_{existing_dir_num}')
            save_path.mkdir()
            print(f"{save_path} has been created.")
        else:
            save_root.mkdir(parents=True)
            print(f"{save_root} has been created.")
            save_path = save_root.joinpath(f'{CURRENT_DATE}_0')
            save_path.mkdir()
            print(f"{save_path} has been created.")
        save_paths[summary_type] = save_path
    
    # Concatenate all text in transcripts
    texts = []
    for idx, text_file in enumerate(target_path.iterdir()):
        if text_file.suffix == '.txt':
            print(f"text_file: {text_file.name}")
            
            with open(text_file, 'r') as f:
                text = f.read()
                texts.append(text)
    
    total_text = ' '.join(texts)
    chunks = split_into_chunks(total_text, model_name)

    with open('sent_split_chunk_test.json', 'w') as f:
        json.dump(chunks, f)
    
    # Load prompts
    with open(PROMPTS_PATH, 'r') as f:
        prompts = json.load(f)
        extractive_prompt = prompts['EXTRACTIVE_SUMMARY']
        abstractive_prompt = prompts['ABSTRACTIVE_SUMMARY']
        reduced_prompt = prompts['REDUCED_SUMMARY']
    
    # Create an OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # For extractive summaries
    extractive_summaries = output_summary(
        openai_client=client,
        summary_type='extractive',
        prompt=extractive_prompt,
        model_name=model_name,
        chunks=chunks,
        save_path=save_paths['extractive'],
    )
    
    # total_extractive_text = ' '.join(extractive_summaries)
    # extractive_chunks = split_into_chunks(total_extractive_text, model_name)
    
    # For abstractive summaries
    abstractive_summaries = output_summary(
        openai_client=client,
        summary_type='abstractive',
        prompt=abstractive_prompt,
        model_name=model_name,
        chunks=extractive_summaries,
        # chunks=extractive_chunks,
        save_path=save_paths['abstractive'],
    )
    
    total_abstractive_text = ' '.join(abstractive_summaries)
    total_abstractive_num_tokens = num_tokens_from_string(total_abstractive_text, model_name)
    prompt_limit = MODELS_INFO[model_name]['prompt_limit']
    
    if total_abstractive_num_tokens > prompt_limit:
        reduced_summaries = output_summary(
            openai_client=client,
            summary_type='reduced',
            prompt=reduced_prompt.replace('{{N}}', prompt_limit),
            model_name=model_name,
            chunks=[total_abstractive_text],
            save_path=save_paths['reduced'],
        )
    else:
        print(f"{save_paths['reduced']} has been removed.")
        shutil.rmtree(save_paths['reduced'])
        
        
    # extractive_summaries = []
    # with open(save_paths['extractive'].joinpath('summaries.json'), 'w') as ewf:
    #     for chunk in chunks:
    #         extractive_prompt_chunk = extractive_prompt
    #         extractive_prompt_chunk = extractive_prompt_chunk\
    #             .replace('{{TEXT}}', chunk)
    #         summary_dic = generate_output(client, model_name, extractive_prompt_chunk)
            
    #         choice = summary_dic['choices'][0] # Fixed choice
    #         extractive_summaries.append(choice['message']['content'])
    #         json.dumps(summary_dic, ewf)
            
    #         # Continue the answer if the answer was stopped due to the length (but only once)
    #         if choice['finish_reason'] == 'length':
    #             print(f"The output has been cut due to its long length. Continue the output.")
    #             stopped_content = choice['message']['content']
    #             extractive_long_prompt = extractive_prompt_chunk + ' Your answer: ' + stopped_content + ' Your answer was stopped due to the length. Please continue your answer.'
    #             summary_dic = generate_output(client, model_name, extractive_long_prompt)
                
    #             extractive_summaries.append(summary_dic['choices'][0]['message']['content'])
    #             json.dumps(summary_dic, ewf)
    
    # total_extractive_text = ' '.join(extractive_summaries)
    # extractive_chunks = split_into_chunks(total_extractive_text, model_name)
    
    # # For abstractive summaries
    # abstractive_summaries = []
    # with open(save_paths['abstractive'].joinpath('summaries.json'), 'w') as awf:
        
    #     for chunk in extractive_chunks:
    #         abstractive_prompt_chunk = abstractive_prompt
    #         abstractive_prompt_chunk = abstractive_prompt_chunk\
    #             .replace('{{N}}', ABSTRACTIVE_PROMPT_N_LIMIT)\
    #             .replace('{{TEXT}}', chunk)
    #         summary_dic = generate_output(client, model_name, abstractive_prompt_chunk)
            
    #         choice = summary_dic['choices'][0] # Fixed choice
    #         abstractive_summaries.append(choice['message']['content'])
    #         json.dumps(summary_dic, awf)
            
    #         # Continue the answer if the answer was stopped due to the length (but only once)
    #         if choice['finish_reason'] == 'length':
    #             print(f"The output has been cut due to its long length. Continue the output.")
    #             stopped_content = choice['message']['content']
    #             abstractive_long_prompt = abstractive_prompt_chunk + ' Your answer: ' + stopped_content + ' Your answer was stopped due to the length. Please continue your answer.'
    #             summary_dic = generate_output(client, model_name, abstractive_long_prompt)
                
    #             abstractive_summaries.append(summary_dic['choices'][0]['message']['content'])
    #             json.dumps(summary_dic, awf)

                
def output_summary(
    openai_client, 
    summary_type: str, 
    prompt: str,
    model_name: str,
    chunks: List[str],
    save_path: Path, 
) -> List[str]:
    """Generate a summary with the given text.

    Args:
        openai_client: An OpenAI client with an API key.
        summary_type (str): A summary_type should be one of 'extractive' or 'abstractive'.
        prompt (str): A base prompt.
        model_name (str): An OpenAI's model name.
        chunks (List[str]): A list of chunks.
        save_path (Path): A path to save a json file.

    Returns:
        List[str]: A list of summaries.
    """

    assert summary_type in ['extractive', 'abstractive', 'reduced'], f"A summary_type should be one of ['extractive', 'abstractive', 'reduced']."

    summaries = []
    with open(save_path.joinpath(f'summaries_{round(time.time())}.json'), 'w') as wf:
        
        for chunk in chunks:
            prompt_chunk = prompt
            prompt_chunk = prompt_chunk.replace('{{TEXT}}', chunk)
            
            if summary_type == 'abstractive':
                prompt_chunk = prompt_chunk.replace('{{N}}', str(ABSTRACTIVE_PROMPT_N_LIMIT))
                system_prompt = prompt_chunk.split('\n\n### Text')[0]
                user_prompt = '\n\n### Text' + prompt_chunk.split('\n\n### Text')[1]
            elif summary_type == 'extractive':
                system_prompt = prompt_chunk.split('\n\n### Text')[0]
                user_prompt = '\n\n### Text' + prompt_chunk.split('\n\n### Text')[1]
            elif summary_type == 'reduced':
                system_prompt = prompt_chunk.split('condense: ')[0] + 'condense: '
                user_prompt = prompt_chunk.split('condense: ')[1]
            
            summary_dic = generate_output(openai_client, model_name, system_prompt, user_prompt)
            
            choice = summary_dic['choices'][0] # Fixed choice
            summaries.append(choice['message']['content'])
            json.dump(summary_dic, wf)
            wf.write('\n')
            
            # Continue the answer if the answer was stopped due to the length (but only once)
            if choice['finish_reason'] == 'length':
                print(f"The output has been cut due to its long length. Continue the output.")
                stopped_content = choice['message']['content']
                long_prompt = prompt_chunk + ' Your answer: ' + stopped_content + ' Your answer was stopped due to the length. Please continue your answer.'
                summary_dic = generate_output(openai_client, model_name, long_prompt, '')
                
                summaries.append(summary_dic['choices'][0]['message']['content'])
                json.dump(summary_dic, wf)
                wf.write('\n')
    
    return summaries
    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder_name', type=str)
    parser.add_argument('-m', '--model_name', type=str, default='gpt-4-1106-preview')
    
    args = parser.parse_args()
    
    main(
        args.folder_name,
        args.model_name,
    )