# import os
# os.system('pip install ibm-watson-machine-learning --upgrade')
import argparse
import yaml
import ast

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy Code Packages')

    parser.add_argument('--yaml_file', '-y', type=str,
                        default='configuration_cpdaas_batch.yaml')

    parser.add_argument(
        '--test_run', '-t',
        default = 'True',
        help='True or False flag, input should be either "True" or "False".',
        type=ast.literal_eval,
        dest='test_run'
    )
    args = parser.parse_args()

    yaml_file = args.yaml_file
    test_run = args.test_run

    # Read YAML file
    print('\n\rLoading configuration yaml file:',yaml_file)
    with open(yaml_file, 'r') as stream:
        configuration = yaml.safe_load(stream)

    # print(configuration)

    wml_credentials = configuration['wml_credentials']
    deployment_info = configuration['deployment_info']
    prj_info = configuration['prj_info']
    if "email_setting" in configuration:
        email_setting = configuration['email_setting']
        print('\n\rsend_email_when_fail: ',email_setting['send_email_when_fail'])
        print('send_email_when_successful: ', email_setting['send_email_when_successful'])
    else:
        email_setting = []
        print('\n\rEmail not enabled')


    print('\n\rCode Package to be deployed:')
    print(prj_info,'\n\r')

    # step 1: login to wml
    from deployment_api import wml_login
    wml_client = wml_login(wml_credentials)

    space_id = deployment_info['space_id']
    wml_client.set.default_space(space_id)
    print("\n\rSet space id successfully:", space_id)

    # From cpd 4.x, deployment function can get the token inside. Hence we don't need password as parameters anymore.
    if "version" in wml_credentials:
        version = wml_credentials['version']
        if version[0]>'3':
            # remove credentials to avoid disclosure of the password.
            if "password" in wml_credentials:
                del wml_credentials['password']

    # This is a generator code needed by CP4D to run your code. In most cases, you don't have to modify it.
    def my_deployable_function(wml_credentials=wml_credentials, deployment_info=deployment_info, prj_info=prj_info,
                               email_setting=email_setting):

        # get USER_ACCESS_TOKEN directly without leaking token, username and password in the deployment function
        if "version" in wml_credentials:
            version = wml_credentials['version']
            if version[0] > '3':
                import os
                user_token = os.environ["USER_ACCESS_TOKEN"]
                wml_credentials['token'] = user_token

        if email_setting:
            send_email_when_successful = email_setting['send_email_when_successful']
            send_email_when_fail = email_setting['send_email_when_fail']
            sender = email_setting['sender']
            receivers = email_setting['receivers']
            smtp_server = email_setting['smtp_server']
        else:
            send_email_when_successful = False
            send_email_when_fail = False

        import subprocess
        import os

        from ibm_watson_machine_learning import APIClient
        wml_client = APIClient(wml_credentials)

        space_id = deployment_info['space_id']
        wml_client.set.default_space(space_id)

        def get_assets_dict():
            assets_dict = {x["metadata"]["name"]: x["metadata"]["asset_id"] for x in
                           wml_client.data_assets.get_details()["resources"]}
            return assets_dict

        import smtplib
        def send_email(smtp_server, sender, receivers, message):
            try:
                smtpObj = smtplib.SMTP(smtp_server)
                smtpObj.sendmail(sender, receivers, message)
                print("Notification Email Sent Successfully")
            # except SMTPException:
            except:
                print("Error: unable to send email")

        def get_date_str():
            from datetime import datetime
            date_str = datetime.now().strftime("%Y-%m-%d")
            return date_str

        date_str = get_date_str()

        assets_dict = get_assets_dict()

        # prj_info = params["prj_info"]
        code_dir_basename = os.path.basename(prj_info['code_dir'])
        tar_file_name = code_dir_basename + ".tar.gz"
        wml_client.data_assets.download(assets_dict[tar_file_name], tar_file_name)
        # for f in params["required_files"]: wml_client.data_assets.download(assets_dict[f], f)

        subprocess.run(["tar", "xzf", tar_file_name])

        def score(payload):
            # output = subprocess.run(["python", prj_info['main_file']], capture_output=True, text=True).stdout

            import json
            # save payload into a local JSON file named as input.json
            input_json_file = 'input.json'
            print('\n\rSaving payload into local JSON file:', input_json_file)
            # Directly from dictionary
            with open(input_json_file, 'w') as infile:
                json.dump(payload, infile)

            # create a dummy output.json
            output_json_file = 'output.json'
            with open(output_json_file, 'w') as outfile:
                json.dump({'output': "none"}, outfile)

            p = subprocess.run(["python", prj_info['main_file']], capture_output=True, text=True)
            # print('exit status:', p.returncode)

            # load output from a JSON file: output.json
            print('\n\rLoading payload from local JSON file:', output_json_file)
            # Directly from dictionary
            with open(output_json_file, 'r') as outfile:
                payload_output = json.load(outfile)
                # payload_output_str = json.dumps(payload_output, indent=4, ensure_ascii=False)

            print('output json=\n', payload_output)

            stdout = p.stdout
            # print('stdout:', stdout)
            stderr = p.stderr
            # print('stdout:', stderr)

            if p.returncode:

                if send_email_when_fail:
                    ############### send email with error msg ##################
                    message = """Subject: {} Error happened\r\n

                            Receipients: {}

                            This message is sent from Cloud Pak for Data platform.

                            ### Start of Error Message ###

                            {}

                            ### End of Error Message ###""".format(date_str, receivers, stderr)

                    send_email(smtp_server, sender, receivers, message)

                values = {"stderr": stderr, "stdout": stdout}

            else:

                if send_email_when_successful:
                    ############### send successful notification ###############
                    message = """Subject: {} Job has completed successfully\r\n

                    Receipients: {}

                    This message is sent from Cloud Pak for Data platform.

                    ### Start of Message ###

                    {}

                    ### End of Message ###""".format(date_str, receivers, stdout)

                    send_email(smtp_server, sender, receivers, message)

                # for online application, we may want to omit the stdout to reduce the unnecessary traffic
                omit_stdout = deployment_info['omit_stdout']
                if omit_stdout:
                    values = {"output": payload_output}
                else:
                    values = {"stdout": stdout, "output": payload_output}

                #return {"predictions": [values]} # not work
                #return {"predictions": [{"values": [stderr]}]} # work

            return {"predictions": [{"values": [values]}]}  # work
        return score


    # step 2: upload_code_2_deployment_space
    from deployment_api import upload_code_2_deployment_space
    upload_code_2_deployment_space(wml_client, prj_info)


    # # Optional: test locally
    # payload = {
    #     "input_data": [{
    # #         "fields": ["keywords"],
    #         "values": []
    #     }]
    # }
    # function_result = my_deployable_function(wml_credentials, space_id, prj_info)(payload)
    # print(function_result)

    # step 3: deploy
    from deployment_api import deploy
    function_deployment_id = deploy(wml_client, my_deployable_function, deployment_info)


    # to do --- clean
    # remove tar file


    # # step 4: run the job
    # payload = {
    #   "input_data": [
    #     {
    #       "fields": [],
    #       "values": [1] # 1 is a dummy input that needed
    #     }
    #   ]
    # }
    #
    #
    # # below code is a reference if you want to schedule job externally using 3rd tool, eg Control M
    # if test_run:
    #     # run online application
    #     # result = wml_client.deployments.score(function_deployment_id, payload)
    #     # if "error" in result:
    #     #     print(result["error"])
    #     # else:
    #     #     print(result)
    #
    #     # for batch job
    #
    #     job = wml_client.deployments.create_job(function_deployment_id, meta_props=payload)
    #     job_id = wml_client.deployments.get_job_uid(job)
    #     print('\n\rjob_id: "%s" successfully submitted'%job_id)
    #     wml_client.deployments.get_job_details(job_id)

    # step 4: run the job
    if test_run:
        deploy_mode = deployment_info['deploy_mode']
        payload = {
            "input_data": [
                {
                    "fields": [],
                    "values": [1]  # 1 is a dummy input that needed
                }
            ]
        }

        # run online application
        if deploy_mode == 'online':
            result = wml_client.deployments.score(function_deployment_id, payload)
            print('result=\n', result)

        # for batch job
        # below code is a reference if you want to schedule job externally using 3rd tool, eg Control M
        else:
            job = wml_client.deployments.create_job(function_deployment_id, meta_props=payload)
            job_id = wml_client.deployments.get_job_uid(job)
            print('\n\rjob_id: "%s" successfully submitted' % job_id)
            wml_client.deployments.get_job_details(job_id)

