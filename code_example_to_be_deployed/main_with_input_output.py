# This is an example code for applications with input and output, usually needed for online application
# You must load your input from "input.json" from the same folder that main python file sit with.
# You must also dump your output to "output.json" to the same folder that main python file sit with.
# If necessary, feel free to modify the code to make input/output filename and location configurable.

import json

def your_own_process(input_json):
    # in the example, output is simply equal to input
    # but in real project, you can do whatever the process, including ML inference
    # make sure your output is in JSON format that you can consume in your own applications.

    output_json = input_json

    return output_json

# Must read input from a JSON file
input_json_file = 'input.json'
print('\n\rLoading payload from local JSON file:',input_json_file)
with open(input_json_file, 'r') as infile:
    payload_input = json.load(infile)

print('input json=\n',payload_input)

output_json = your_own_process(payload_input)

# MUST save output to a JSON file
output_json_file = 'output.json'
print('\n\rSaving payload into local JSON file:',output_json_file)
with open(output_json_file, 'w') as outfile:
    json.dump(output_json, outfile)