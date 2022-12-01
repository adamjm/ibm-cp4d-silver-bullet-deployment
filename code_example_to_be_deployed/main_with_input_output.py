# This is an example code for applications with input and output, usually needed for online application
# You must load your input from "input.json" from the same folder that main python file sit with.
# Your output must be in JSON format and you must also dump your output JSON to stderr which will be processed.

# input JSON format must have "input_data" and "values", an example below
# {"input_data":[{
#         "fields":["AGE","SEXE"],
#         "values":[
#             [33,"F"],
#             [59,"F"],
#             [28,"M"]
#             ]
#         }]}


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

def loadInputData() :
    data_len = 0
    json_data = []
    if select.select([sys.stdin, ], [], [], 0.0)[0]:
        data1 = sys.stdin.readlines()
        try:
            data_len = len(data1)
            for i in range(len(data1)) :
                _json_data = json.loads(data1[i])
                json_data.append(_json_data)
            msg = "Data loaded"
        except Exception as e :
            msg = "Err loading data :" + str(e)
            json_data = data1
    else:
        msg = "No data"
    #jsondata={"values": [[33,"F",data,json_data,[1,33],[9,41],[0.18,0.82],1,"O"]]}
    jsondata={"status": msg, "json_data" : json_data, "data_len":data_len}
    print(jsondata)
    return jsondata


def load_input_json():
    data = json.load(sys.stdin)
    print('Input JSON data loaded')
    return data

def your_own_process(input_json):
    # output must be in JSON format
    # in the example, output is simply equal to input
    # but in real project, you can do whatever in the process, including ML inference

    output_json = input_json

    #output_json = json.dumps(output_json, indent=4, ensure_ascii=False)

    return output_json


if __name__ == '__main__':

    print('Start your application')

    # data = loadInputData()
    data = load_input_json()

    output_json = your_own_process(data)
    print('Output JSON data generated')

    # Here stderr is used to save your output result
    # stdout is used to all your normal print
    # xx
    eprint(output_json, end='')

    # json_string = json.dumps(output_json, ensure_ascii=False)
    # sys.stderr.write(json_string)

