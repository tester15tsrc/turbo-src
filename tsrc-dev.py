import os
import json
import subprocess
import argparse
import requests
import re
import traceback
import sys
import time
import random
from requests.exceptions import ConnectionError

def usage():
    print("Usage: script.py [init USERNAME REPO ACTION]")
    print("  init: initialize necessary files and directories")
    exit(1)

def initialize_files():
    with open('./turbosrc.config', 'r') as f:
        config_data = json.load(f)

    USER = config_data.get('GithubName', None)
    GITHUB_API_TOKEN = config_data.get('GithubApiToken', None)
    SECRET = config_data.get('Secret', None)
    ADDR = config_data.get('TurboSrcID', None)
    MODE = config_data.get('Mode', None)

    if ADDR:
        if not is_valid_ethereum_address(ADDR):
            ADDR = None
    else:
        ADDR = None

    if MODE in ['local', 'router-host']:
        URL = "http://turbosrc-service:4000/graphql"
    elif MODE == 'router-client':
        URL = ""

    if None in (USER, GITHUB_API_TOKEN, SECRET, MODE):
        raise ValueError("Failed to initialize files: not all required parameters found in turbosrc.config")

    os.makedirs('./GihtubMakerTools', exist_ok=True)
    os.makedirs('./fork-repo', exist_ok=True)
    os.makedirs('./create_pull_requests', exist_ok=True)
    os.makedirs('./turbosrc-service', exist_ok=True)

    with open('./GihtubMakerTools/ght.ini', 'w') as f:
        f.write(f"[github.org]\nUser = {USER}\nToken = {GITHUB_API_TOKEN}\nOrganization =")

    with open('./fork-repo/env.list', 'w') as f:
        f.write(f"GITHUB_TOKEN={GITHUB_API_TOKEN}")

    with open('./create_pull_requests/env.list', 'w') as f:
        f.write(f"GITHUB_TOKEN={GITHUB_API_TOKEN}")

    config = {
        "github": {
            "organization": "turbo-src",
            "user": USER,
            "apiToken": GITHUB_API_TOKEN
        },
        "turbosrc": {
            "endpoint": {
              "mode": "online",
              "url": URL,
              "egressURLoption": URL
            },
            "jwt": SECRET,
            "store": {
                "repo": {
                    "addr": "REPO_ADDR",
                    "key": "REPO_KEY"
                },
                "contributor": {
                    "addr": ADDR,
                    "key": "YOUR_KEY"
                }
            }
        },
        "offchain": {
            "endpoint": {
                "mode": "online",
                "url": "http://turbosrc-engine:4002/graphql"
            }
        },
        "namespace": {
            "endpoint": {
                "mode": "online",
                "url": "http://namespace-service:4003/graphql"
            }
        },
        "gh": {
            "endpoint": {
                "mode": "online",
                "url": "http://gh-service:4004/graphql"
            }
        },
        "testers": {}
    }

    with open('./turbosrc-service/.config.json', 'w') as f:
        json.dump(config, f, indent=4)

    return MODE

def update_api_token():
    with open('./turbosrc-service/.config.json', 'r') as f:
        data = json.load(f)

    apiToken = data['github']['apiToken']

    with open('./turbosrc.config', 'r') as f:
        turbosrcConfigData = json.load(f)
    with open('./turbosrc-service/.config.json', 'r') as f:
        serviceConfigData = json.load(f)

    secret = turbosrcConfigData.get('Secret')

    decryptedToken = subprocess.check_output([
        'docker-compose', 'run', '--rm', 'jwt_hash_decrypt', '--secret=' + secret, '--string={\"githubToken\": \"' + apiToken + '\"}'
    ]).decode('utf-8').split('\n')[-2]

    serviceConfigData['github']['apiToken'] = decryptedToken

    with open('./turbosrc-service/.config.json', 'w') as f:
        json.dump(serviceConfigData, f, indent=4)

def is_valid_ethereum_address(address):
    try:
        return bool(re.match("^0x[a-fA-F0-9]{40}$", address))
    except Exception as e:
        print(f"Failed to check if provided string is a valid Ethereum address. Error: {str(e)}")
        traceback.print_exc()
        return False

def get_contributor_id():
    last_exception = None
    try:
        with open('./turbosrc-service/.config.json', 'r') as f:
            data = json.load(f)

        url = 'http://localhost:4003'  # data['namespace']['endpoint']['url']
        token = data['github']['apiToken']
        contributor_name = data['github']['user']

        query = f"""
        {{
            findOrCreateUser(owner: "", repo: "", contributor_id: "none", contributor_name: "{contributor_name}", contributor_signature: "none", token: "{token}") {{
                contributor_name,
                contributor_id,
                contributor_signature,
                token
            }}
        }}
        """

        max_retries = 5  # Number of attempts before printing an error message

        for i in range(max_retries):
            try:
                response = requests.post(f"{url}/graphql", json={'query': query}, headers={"Content-Type": "application/json", "Accept": "application/json"})
                response.raise_for_status()
                result = response.json()
                if result.get('data') and result['data'].get('findOrCreateUser'):
                    return result['data']['findOrCreateUser']['contributor_id']
            except Exception as e:
                last_exception = e
                if i < max_retries - 1:  # if not the last attempt, skip to the next iteration
                    # exponential backoff with jitter
                    wait_time = (2 ** i) + random.random()
                    time.sleep(wait_time)
                    continue
                else:  # if this is the last attempt, then raise the exception
                    raise last_exception
    except Exception as e:
        print(f"Failed to get contributor id. Error: {str(e)}")
        traceback.print_exc()
        return None

def update_contributor_id(contributor_id):
    try:
        with open('./turbosrc-service/.config.json', 'r') as f:
            data = json.load(f)

        current_address = data['turbosrc']['store']['contributor']['addr']

        if not is_valid_ethereum_address(current_address):
            data['turbosrc']['store']['contributor']['addr'] = contributor_id

            with open('./turbosrc-service/.config.json', 'w') as f:
                json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Failed to update contributor id. Error: {str(e)}")
        traceback.print_exc()

def manage_docker_service(action):
    if action == 'start':
        subprocess.run(['docker-compose', 'up', '-d', 'namespace-service'], check=True)
        max_retries = 30  # maximum attempts to check if the service is up
        retries = 0
        last_error = None
        while retries < max_retries:
            try:
                # Try to fetch contributor id
                contributor_id = get_contributor_id()
                # If fetch is successful, update contributor_id and break from loop
                if contributor_id is not None:
                    update_contributor_id(contributor_id)
                    break
            except ConnectionError as e:
                last_error = e
                # If a connection error occurred, sleep for a while and try again
                time.sleep(2)
                retries += 1
        else:
            # If the loop has exhausted the max_retries without success, print error message and exit
            if last_error is not None:
                print(f"Failed to fetch contributor id. Error: {str(last_error)}. Exiting...")
                sys.exit(1)
    elif action == 'stop':
        subprocess.run(['docker-compose', 'stop', 'namespace-service'], check=True)

def update_turbosrc_id_egress_router_url_in_env_file(env_file_path):
    # load turbosrc.store.contributor from .config.json
    with open('./turbosrc-service/.config.json', 'r') as f:
        service_config_data = json.load(f)

    turbosrc_id = service_config_data.get('turbosrc', {}).get('store', {}).get('contributor', {}).get('addr', None)
    if turbosrc_id is None:
        raise ValueError("'turbosrc.store.contributor' not found in turbosrc-service/.config.json")

    egress_router_url = service_config_data.get('turbosrc', {}).get('endpoint', {}).get('egressURLoption', None)
    if egress_router_url is None:
        raise ValueError("'turbosrc.turbosrc.endpoint' not found in turbosrc-service/.config.json")

    # Read the original lines from the file
    with open(env_file_path, 'r') as f:
        original_lines = f.readlines()

    # Prepare the updated lines
    updated_lines = []
    found_turbosrc_id = False
    found_egress_router_url = False
    for line in original_lines:
        if line.startswith('TURBOSRC_ID'):
            line = f"TURBOSRC_ID={turbosrc_id}\n"
            found_turbosrc_id = True
        if line.startswith('EGRESS_ROUTER_URL'):
            line = f"EGRESS_ROUTER_URL={egress_router_url}\n"
            found_egress_router_url = True
        updated_lines.append(line)

    # If we didn't find a TURBOSRC_ID line, append one
    if not found_turbosrc_id:
        updated_lines.append(f"TURBOSRC_ID={turbosrc_id}\n")
    if not found_egress_router_url:
        updated_lines.append(f"EGRESS_ROUTER_URL={egress_router_url}\n")

    # Write the updated lines back to the file
    with open(env_file_path, 'w') as f:
        f.writelines(updated_lines)

def check_and_create_service_env(env_file_path):
    # Check if the service.env file exists
    if not os.path.exists(env_file_path):
        # If not, create an empty file
        open(env_file_path, 'a').close()

def validate_and_update_endpoint_url():
    with open('./turbosrc.config', 'r') as f:
        config_data = json.load(f)

    mode = config_data.get('Mode', None)

    if mode is not None:
        with open('./turbosrc-service/.config.json', 'r') as f:
            service_config_data = json.load(f)

        service_config_data['turbosrc']['endpoint']['egressURLoption'] = "http://turbosrc-egress-router:4006/graphql"

        if mode in ['local', 'router-host']:
            service_config_data['turbosrc']['endpoint']['url'] = "http://turbosrc-service:4000/graphql"

        if mode == 'router-client':
            service_config_data['turbosrc']['endpoint']['url'] = "http://turbosrc-service:4000/graphql"

        with open('./turbosrc-service/.config.json', 'w') as f:
            json.dump(service_config_data, f, indent=4)

    else:
        raise ValueError("Missing 'Mode' value in 'turbosrc.config'")

def remove_egressURLoption():
    with open('./turbosrc-service/.config.json', 'r') as f:
        config = json.load(f)

    if config.get('turbosrc', {}).get('endpoint', {}).get('egressURLoption', None) is not None:
        del config['turbosrc']['endpoint']['egressURLoption']

        with open('./turbosrc-service/.config.json', 'w') as f:
            json.dump(config, f, indent=4)

def update_egressURLoption():
    with open('./turbosrc-service/.config.json', 'r') as f:
        config = json.load(f)

    if config.get('turbosrc', {}).get('endpoint', {}).get('egressURLoption', None) is not None:
        config['turbosrc']['endpoint']['egressURLoption'] = "https://turbosrc-marialis.dev"

        with open('./turbosrc-service/.config.json', 'w') as f:
            json.dump(config, f, indent=4)

def update_turbosrc_url(url):
    with open('./turbosrc-service/.config.json', 'r') as f:
        config = json.load(f)

    if config.get('turbosrc', {}).get('endpoint', {}).get('url', None) is not None:
        config['turbosrc']['endpoint']['url'] = url
        with open('./turbosrc-service/.config.json', 'w') as f:
            json.dump(config, f, indent=4)

def update_extension_config():
    # 1. Read the contents of `./turbosrc-service/.config.json`.
    with open('./turbosrc-service/.config.json', 'r') as f:
        turbosrc_data = json.load(f)

    # 2. Extract the necessary values from it.
    github_user = turbosrc_data.get('github', {}).get('user')
    turbosrc_id = turbosrc_data.get('turbosrc', {}).get('store', {}).get('contributor', {}).get('addr')

    # Check and raise specific errors if values are not found
    if not github_user:
        raise ValueError("github.user field not found in turbosrc-service/.config.json.")
    if not turbosrc_id:
        raise ValueError("turbosrc.store.contributor.addr field not found in turbosrc-service/.config.json.")

    # 3. Write the new fields and values into `./chrome-extension/config.devOnline.json`.
    with open('./chrome-extension/config.devOnline.json', 'r') as f:
        dev_online_data = json.load(f)

    dev_online_data['myGithubName'] = github_user
    dev_online_data['myTurboSrcID'] = turbosrc_id

    with open('./chrome-extension/config.devOnline.json', 'w') as f:
        json.dump(dev_online_data, f, indent=4)

parser = argparse.ArgumentParser()
parser.add_argument("operation", help="Operation to perform: 'init' initializes necessary files and directories")

args = parser.parse_args

if __name__ == "__main__":
    args = parser.parse_args()
    if args.operation.lower() == 'init':
        # upfront or docker-compose commands fail.
        check_and_create_service_env('./turbosrc-ingress-router/service.env')
        check_and_create_service_env('./turbosrc-egress-router/service.env')

        MODE = initialize_files()
        update_api_token()
        manage_docker_service('start')
        manage_docker_service('stop')
        validate_and_update_endpoint_url()
        update_turbosrc_id_egress_router_url_in_env_file('./turbosrc-ingress-router/service.env')
        update_turbosrc_id_egress_router_url_in_env_file('./turbosrc-egress-router/service.env')
        if MODE != 'router-client':
            remove_egressURLoption()
        if MODE == 'router-client':
            update_egressURLoption()
            update_turbosrc_id_egress_router_url_in_env_file('./turbosrc-ingress-router/service.env')
        if MODE == 'router-host':
            update_turbosrc_url("http://turbosrc-egress-router:4006/graphql")
        try:
            update_extension_config()
        except ValueError as e:
            print(f"Error: {e}")

    else:
        usage()
