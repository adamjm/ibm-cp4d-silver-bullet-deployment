# This is an example code for applications with input and output, usually needed for online application
# You must load your input from "input.json" from the same folder that main python file sit with.
# Your output must be in JSON format and you must also dump your output JSON to stderr which will be processed.



import os
import warnings
import json
import sys
import select

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
#         "fields":["AGE","SEXE"],
#         "values":[
#             [33,"F"],
#             [59,"F"],
#             [28,"M"]
#             ]
#         }]}
def load_input_json():
    data = json.load(sys.stdin)
    print('Input JSON data loaded')
    return data

# Output must be in JSON format
# Users can define their own output, as long as it can be processed by their own applications.
def your_own_process(input_json):
    # example 1)
    # In the example, output is simply equal to input
    # In real project, you can do whatever in the process, including ML inference
    # output_json = input_json

    # example 2)
    # If want to be consist with model deployment, output JSON should have "fields" and "values".
    # Example below:
    output_json = {
      "fields": [
        "prediction_classes",
        "probability"
      ],
      "values": [
        [
          7,
          [
            0.9999523162841797,
            8.347302582478733e-08
          ]
        ],
        [
          2,
          [
            8.570060003876279e-07,
            0.9999991655349731
          ]
        ]
      ]
    }

    return output_json


if __name__ == '__main__':

    print('Start your application')

    data = load_input_json()

    output_json = your_own_process(data)
    print('Output JSON data generated')

    # Here stderr is used to save your output result
    eprint(output_json, end='')


