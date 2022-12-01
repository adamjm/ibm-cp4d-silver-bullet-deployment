from subprocess import run
import json,ast

# prepare your own input
payload = {"input_data":[{
        "fields":["AGE","SEXE"],
        "values":[
            [33,"F"],
            [59,"F"],
            [28,"M"]
            ]
        }]}

# make sure input is in a proper JSON format
json_string=json.dumps(payload, ensure_ascii=False)

# run your main python program with input from stdio, to mimic the behavior of CP4D deployment
p = run(["python", '-i', 'main_with_input_output.py'], capture_output=True, input=json_string, text=True)

# normal print from stdout
run_log = p.stdout
print('\nRunning log:')
print('--------------------------------------------------------------------')
print(run_log)

# output JSON saved in stderr
output_json = p.stderr
# remove ending dummy output
idx = output_json.find('>>>', 0)
output_json = output_json[:idx]
# print('\noutput_json:\n', output_json)

# confirm output is in JSON format
print('\nOutput JSON status:')
print('--------------------------------------------------------------------')
try:
    jsondata = ast.literal_eval(output_json)
    print("JSON String found on output: \n", output_json)
except Exception as e:
    jsondata = {"info": ["JSON String not found on output: ", output_json]}
    print("JSON String not found on output: \n", output_json)







