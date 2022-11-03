# You must deploy your job before you can run your job using below code.
import argparse
import yaml


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy Code Packages')

    parser.add_argument('--yaml_file', '-y', type=str,
                        default='configuration_cpd45_dbaccess.yaml')

    parser.add_argument('--function_deployment_id', '-f', type=str,
                        default='4387d483-7f25-4653-a5e3-e996fb23e197')

    args = parser.parse_args()

    yaml_file = args.yaml_file

    # setting function_deployment_id which is obtained from a successful deployment
    function_deployment_id = args.function_deployment_id

    # # Read YAML file
    # with open(args.yaml_file, 'r') as stream:
    #     configuration = yaml.safe_load(stream)
    #
    # wml_credentials = configuration['wml_credentials']
    # deployment_info = configuration['deployment_info']
    # prj_info = configuration['prj_info']
    # email_setting = configuration['email_setting']
    #
    # # login to wml
    # from deployment_api import wml_login
    # wml_client = wml_login(wml_credentials)
    # # set space id
    # space_id = deployment_info['space_id']
    # wml_client.set.default_space(space_id)

    # Read YAML file
    print('\n\rLoading configuration yaml file:', yaml_file)
    with open(yaml_file, 'r') as stream:
        configuration = yaml.safe_load(stream)

    # print(configuration)

    wml_credentials = configuration['wml_credentials']
    deployment_info = configuration['deployment_info']

    # step 1: login to wml
    from deployment_api import wml_login
    wml_client = wml_login(wml_credentials)

    space_id = deployment_info['space_id']
    wml_client.set.default_space(space_id)
    print("\n\rSet space id successfully:", space_id)


    # step 4: run the job
    payload = {
      "input_data": [
        {
          "fields": [],
          "values": [1] # 1 is a dummy input that needed
        }
      ]
    }

    # run online application
    # result = wml_client.deployments.score(function_deployment_id, payload)
    # if "error" in result:
    #     print(result["error"])
    # else:
    #     print(result)

    # for batch job
    job = wml_client.deployments.create_job(function_deployment_id, meta_props=payload)
    job_id = wml_client.deployments.get_job_uid(job)
    print('\n\rjob_id: "%s" successfully submitted'%job_id)
    wml_client.deployments.get_job_details(job_id)
