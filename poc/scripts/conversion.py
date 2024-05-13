import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from openai import OpenAI
from dotenv import dotenv_values
from utils import MODELS_INFO, split_into_chunks, generate_output

# Global variables
CURRENT_DATE = datetime.now().strftime('%Y%m%d')
SUMMARY_PATH = Path(__file__).parent.parent.joinpath('data', 'summary')
PROMPTS_PATH = Path(__file__).parent.parent.joinpath('prompts', 'convert_prompts.json')
OPENAI_API_KEY = dotenv_values(Path(__file__).parent.parent.parent.joinpath('.env'))['OPENAI_API_KEY']
TREE_PATH = Path(__file__).parent.parent.joinpath('data', 'tree')

if not TREE_PATH.exists():
    TREE_PATH.mkdir()
    print(f"{TREE_PATH} has been created.")

def main(
    folder_name: str,
    date_index: str,
    model_name: str,
):
    assert model_name in MODELS_INFO, f"{model_name} is not allowed.\nModel candidates are {', '.join(MODELS_INFO.keys())}."
    
    if date_index == '':
        reduced_directories = [p for p in SUMMARY_PATH.joinpath(folder_name, 'reduced').iterdir() if p.is_dir()]
        if len(reduced_directories) == 0:
            abstractive_directories = [p for p in SUMMARY_PATH.joinpath(folder_name, 'abstractive').iterdir() if p.is_dir()]
            if len(abstractive_directories) == 0:
                raise NameError(f"There is no abstractive summary.")
            abstractive_directories.sort(key= lambda x: x.name)
            target_path = SUMMARY_PATH.joinpath(folder_name, 'abstractive', abstractive_directories[-1].name)
        else:
            reduced_directories.sort(key=lambda x: x.name)
            target_path = SUMMARY_PATH.joinpath(folder_name, 'reduced', reduced_directories[-1].name)
    else:
        target_path = SUMMARY_PATH.joinpath(folder_name, 'reduced', date_index)
        if not target_path.exists():
            target_path = SUMMARY_PATH.joinpath(folder_name, 'abstractive', date_index)
            if not target_path.exists():
                raise NameError(f"{target_path} does not exist.")
            
    # Check save paths
    save_paths = {'hierarchical': '', 'json': ''}
    for tree_type in save_paths.keys():
        save_root = TREE_PATH.joinpath(folder_name, tree_type)
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
        save_paths[tree_type] = save_path
    
    texts = []
    print(f"target_path: {target_path}")
    with open([p for p in target_path.iterdir() if p.suffix == '.json'][0], 'r') as f:
        for line in f:
            tmp_dic = json.loads(line)
            texts.append(tmp_dic['choices'][0]['message']['content'])
            
    total_text = ' '.join(texts)

    # Load prompts    
    with open(PROMPTS_PATH, 'r') as f:
        prompts = json.load(f)
        hierarchical_tree_prompt = prompts['HIERARCHICAL_TREE_PROMPT']
        json_tree_prompt = prompts['JSON_TREE_PROMPT']
    
    # Create an OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # For hierarchical tree
    hierarchical_tree = output_tree(
        openai_client=client,
        tree_type='hierarchical',
        prompt=hierarchical_tree_prompt,
        prompt_material=total_text,
        model_name=model_name,
        save_path=save_paths['hierarchical'],
    )
    
    total_hierarchical_tree = ' '.join(hierarchical_tree)
    
    # For json tree
    json_tree = output_tree(
        openai_client=client,
        tree_type='json',
        prompt=json_tree_prompt,
        prompt_material=total_hierarchical_tree,
        model_name=model_name,
        save_path=save_paths['json'],
    )
    
    total_json_tree = ''.join([j.replace('```json\n', '').replace('`', '') for j in json_tree])
    
    with open(save_paths['json'].joinpath('data.js'), 'w') as f:
        f.write(total_json_tree)
    

def output_tree(
    openai_client, 
    tree_type: str, 
    prompt: str,
    prompt_material: str,
    model_name: str,
    save_path: Path, 
):
    
    assert tree_type in ['hierarchical', 'json'], f"A tree_type should be one of ['hierarchical', 'json']."

    outputs = []
    with open(save_path.joinpath(f'tree_{round(time.time())}.json'), 'w') as wf:
        
        if tree_type == 'hierarchical':
            prompt = prompt.replace('{{TEXT}}', prompt_material)
            system_prompt = prompt.split('\n\n### Text Material')[0]
            user_prompt = '\n\n### Text Material' + prompt.split('\n\n### Text Material')[1]
        elif tree_type == 'json':
            prompt = prompt.replace('{{TREE}}', prompt_material)
            system_prompt = prompt.split('\n\n### Tree Structure')[0]
            user_prompt = '\n\n### Tree Structure' + prompt.split('\n\n### Tree Structure')[1]
            
        tree_dic = generate_output(openai_client, model_name, system_prompt, user_prompt)
        finish_reason = tree_dic['choices'][0]['finish_reason']
        json.dump(tree_dic, wf)
        outputs.append(tree_dic['choices'][0]['message']['content'])
        
        while finish_reason != 'stop':
            print(f"The output has been cut due to its long length. Continue the output.")
            stopped_content = tree_dic['choices'][0]['message']['content']
            prompt += ' Your answer: '
            prompt += stopped_content
            prompt += ' Your answer was stopped due to the length. Please continue your answer.'
            
            tree_dic = generate_output(openai_client, model_name, prompt, '')
            finish_reason = tree_dic['choices'][0]['finish_reason']
            json.dump(tree_dic, wf)
            outputs.append(tree_dic['choices'][0]['message']['content'])
            
        print(f"Outputting {tree_type} tree has been completed.")
    
    return outputs
        


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder_name', type=str)
    parser.add_argument('-i', '--date_index', type=str, default='')
    parser.add_argument('-m', '--model_name', type=str, default='gpt-4-1106-preview')
    
    args = parser.parse_args()
    
    main(
        args.folder_name,
        args.date_index,
        args.model_name,
    )