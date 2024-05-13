import json
import tiktoken
from typing import List, Dict
from sentsplit.segment import SentSplit

# OpenAI Models Information - 04/10/2024
# Set the prompt limit smaller than the original to continue the answer when we have longer response
MODELS_INFO = {
    'gpt-4-turbo': {
        'prompt_limit': 2000, # original: 128000
        'output_limit': 4096,
    },
    'gpt-4-1106-preview': {
        'prompt_limit': 2000, # original: 128000
        'output_limit': 4096,
    },
    'gpt-3.5-turbo': {
        'prompt_limit': 2000, # original: 16385
        'output_limit': 4096,
    },
    'gpt-3.5-turbo-instruct': {
        'prompt_limit': 2000, # original: 4096
        'output_limit': 4096,
    }
}

def num_tokens_from_string(string: str, model_name: str) -> int:
    """Get the number of tokens of a given string.

    Args:
        string (str): A target string.
        model_name (str): An OpenAI's model.

    Returns:
        int: The number of tokens.
    """
    
    assert model_name in MODELS_INFO, f"{model_name} is not allowed.\nModel candidates are {', '.join(MODELS_INFO.keys())}."
    
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def split_into_chunks(text: str, model_name: str) -> List[str]:
    """Split the text into smaller chunks.

    Args:
        text (str): A string of text.
        model_name (str): An OpenAI model.

    Returns:
        List[str]: A list of chunks.
    """
    
    assert model_name in MODELS_INFO, f"{model_name} is not allowed.\nModel candidates are {', '.join(MODELS_INFO.keys())}."
    
    prompt_limit = MODELS_INFO[model_name]['prompt_limit']
    print(f"model name: {model_name}, prompt limit: {prompt_limit}")
    total_num_tokens = num_tokens_from_string(text, model_name)
    
    if total_num_tokens <= prompt_limit:
        # Return the original text if it is shorter than token limit
        return [text]
    else:
        # Initialize a sentence splitter
        sent_splitter = SentSplit('en')
        
        # Split text into sentences
        sentences = sent_splitter.segment(text)
        print(f"num of sentences: {len(sentences)}")
        
        sentences_num_tokens = list(map(lambda s: num_tokens_from_string(s, model_name), sentences))
        print(f"partial sentences_num_tokens: {sentences_num_tokens[:10]}")
        
        chunks = []
        prev_idx = 0
        temp_num_tokens = 0
        sentences_num = len(sentences)
        for idx, s_num_tokens in enumerate(sentences_num_tokens):
            temp_num_tokens += s_num_tokens
            if temp_num_tokens > prompt_limit:
                print(f"temp_num_tokens: {temp_num_tokens}")
                if (idx - prev_idx) >= 1:
                    temp_chunk = ''.join(sentences[prev_idx:idx])
                    chunks.append(temp_chunk)
                    prev_idx = idx
                    temp_num_tokens = s_num_tokens
                else:
                    print('The current sentence is too long, but added.')
                    temp_chunk = sentences[prev_idx]
                    chunks.append(temp_chunk)
                    prev_idx = idx
                    temp_num_tokens = 0
               
            # The loop reaches to the end without additional chunks
            if (idx == (sentences_num - 1)) and (prev_idx != idx):
                print(f"End without additional chunks")
                temp_chunk = ''.join(sentences[prev_idx:idx])
                chunks.append(temp_chunk)
        
        return chunks

def generate_output(openai_client, model_name: str, system_prompt: str, user_prompt: str) -> Dict:
    """Extract important sentences using an LLM.

    Args:
        openai_client: An OpenAI client.
        model_name (str): A model name used in OpenAI client.
        prompt (str): An extractive prompt.

    Returns:
        Dict: A result dictionary of a response.
    """
    
    messages = []
    if system_prompt != '':
        messages.append({'role': 'system', 'content': system_prompt})
    if user_prompt != '':
        messages.append({'role': 'user', 'content': user_prompt})
    
    assert len(messages) >= 1, f"You must put system or user prompt."
    
    response = openai_client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    print(f"The response was created.")
    
    result_dic = {
        'id': response.id,
        'model': response.model,
        'object': response.object,
        'usage': {
            'completion_tokens': response.usage.completion_tokens,
            'prompt_tokens': response.usage.prompt_tokens,
            'total_tokens': response.usage.total_tokens,
        },
        'choices': [],
    }
    
    # Don't allow other choices
    result_dic['choices'].append({
        'finish_reason': response.choices[0].finish_reason,
        'index': response.choices[0].index,
        'message': {
            'content': response.choices[0].message.content,
            'role': response.choices[0].message.role,
        },
        'logprobs': response.choices[0].logprobs,
    })
    
    return result_dic
    
def test1():
    
    string = "You are the only one I have one I have one I have one I have."
    test_string = string * 10000
    model_name = 'gpt-4-1106-preview'
    test_num_tokens = num_tokens_from_string(test_string, model_name)
    
    print(f"test_num_tokens: {test_num_tokens}")
    
    chunks = split_into_chunks(test_string, model_name)
    print(f"length of chunks: {len(chunks)}")
    
    with open('chunk_test.json', 'w') as f:
        json.dump(chunks, f)
    
def test2():
    
    string1 = "You are the only one I have"
    string2 = "one I have"
    test_string = string1 + string2 * 50000 + '.' + string1 + '.'
    model_name = 'gpt-4-1106-preview'
    test_num_tokens = num_tokens_from_string(test_string, model_name)
    
    print(f"test_num_tokens: {test_num_tokens}")
    
    chunks = split_into_chunks(test_string, model_name)
    print(f"length of chunks: {len(chunks)}")
    
    with open('chunk_test.json', 'w') as f:
        json.dump(chunks, f)


if __name__ == '__main__':
    # test1()
    test2()