# This is an example code for applications with input and output, usually needed for online application
# You must load your input from "input.json" from the same folder that main python file sit with.
# Your output must be in JSON format and you must also dump your output JSON to stderr which will be processed.


# In deployment space, there might be missing python libraries. If so, the first thing is to install missing libraries
# Below is an example to install ibm-watson-machine-learning
import subprocess
# output = subprocess.run(["pip3", "install", "ibm-watson-machine-learning", "--upgrade"], capture_output=True, text=True).stdout
# print(output)

import os
import warnings
import json
import sys

import contextlib
import timeit
import yaml
try:
    # get faster C implementation of SafeLoader
    from yaml import CSafeLoader as SafeLoader
except:
    from yaml import SafeLoader
import torch

# transformers 
from transformers import CodeGenForCausalLM, CodeGenTokenizerFast

warnings.filterwarnings("ignore")

# print to stderr
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def getEnvVariables() :
    vars = {}
    for name, value in os.environ.items():
        vars[name] = value
    return vars

# input JSON format must have "input_data", "fields" and "values", an example below
# more explained in: https://cloud.ibm.com/apidocs/machine-learning#deployments-compute-predictions

# {"input_data":[{
#         "fields":["sas_code"],
#         "values":[
#             ['sas code 1'],
#             ['sas code 2'],
#             ['sas code 3']
#             ]
#         }]}
def load_input_json():
    data = json.load(sys.stdin)
    print('Input JSON data loaded')
    return data


def convert_to_python(sas_code, params_generate, tokenizer, model):
    
    # make the input to model
    input_to_model = f"Translate SAS: <|sepoftext|> {sas_code} <|sepoftext|> to Python: <|sepoftext|>"
    
    # tokenizing input for the model
    tok_kwargs = {'truncation': True, 'max_length': params_generate["model_size"]}
    input_ids = tokenizer(input_to_model, **tok_kwargs, return_tensors='pt').input_ids
    
    
    sep_token_id = tokenizer.sep_token_id
    pad_token_id = tokenizer.pad_token_id
    bos_token_id = tokenizer.bos_token_id
    eos_token_id = tokenizer.eos_token_id

    with torch.no_grad():
        input_ids = input_ids.to(device)
        output_tokens = model.generate(
            input_ids, 
            do_sample=params_generate["do_sample"],
            num_return_sequences=params_generate["nb_samples"],
            temperature=params_generate["temperature"],
            max_new_tokens=params_generate["max_new_tokens"],
            top_p=params_generate["top_p"],
            bos_token_id=bos_token_id,
            eos_token_id=eos_token_id,
            pad_token_id=pad_token_id,
            use_cache=True,
        )
        # printing output of the model (taking only new tokens)
        output_tokens = output_tokens[:, input_ids.shape[1]:]
    
    result = tokenizer.batch_decode(output_tokens, skip_special_tokens=False)[0]
    return result.split(tokenizer.eos_token)[0]

# Output must be in JSON format
# Users can define their own output, as long as it can be processed by their own applications.
def your_own_process(input_json):
    cache_dir="./tmp_cache"
    ckpt_load = "../ckpt_step_999"
    do_sample=False
    temperature=0.2
    top_p=0.95
    nb_samples=1

    # no file, we load content and prompt directly in jupyter
    model_size=1024
    max_new_tokens=500
    zero_shot=False

    tokenizer = CodeGenTokenizerFast.from_pretrained(
    ckpt_load, pad_token='<|pad|>', sep_token='<|sepoftext|>')

    # just add truncation and padding side 
    tokenizer.padding_side = 'left'
    tokenizer.truncation_side = 'left'

    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    # print(device)
    model = CodeGenForCausalLM.from_pretrained(ckpt_load, 
        cache_dir=cache_dir).to(device)
    model.eval()

    # example 1)
    # In the example, output is simply equal to input
    # In real project, you can do whatever in the process, including ML inference
    sas_code = input_json["input_data"]["values"]
    sample_size = len(sas_code)

    params_generate = {
    "do_sample": do_sample,
    "nb_samples": nb_samples,
    "temperature": temperature,
    "max_new_tokens": max_new_tokens,
    "top_p": top_p,
    "model_size": model_size
    }

    py_code = []
    for sc in sas_code:
      pc = convert_to_python(sc, params_generate, tokenizer, model)
      if decoded_output_tokens[0] == ' ':
        decoded_output_tokens = decoded_output_tokens[1:]
        py_code.append([decoded_output_tokens])


    # example 2)
    # If want to be consist with model deployment, output JSON should have "fields" and "values".
    # Example below:
    output_json = {
      "fields": [
        "py_code"
      ],
      "values": py_code
    }

    return output_json


if __name__ == '__main__':

    print('Start your application')

    data = load_input_json()

    output_json = your_own_process(data)
    print('Output JSON data generated')

    # Here stderr is used to save your output result
    eprint(output_json, end='')


