import requests
import xmltodict

# Configuration
vcloud_url = "https://your-vcloud-director-url/api"
username = "your-username"
password = "your-password"
org = "your-org"

# Authenticate and get a session token
def get_vcloud_session():
    headers = {
        'Accept': 'application/*+xml;version=34.0',
        'Authorization': 'Basic ' + (username + '@' + org + ':' + password).encode('utf-8').decode('ascii'),
    }

    response = requests.post(f'{vcloud_url}/sessions', headers=headers)
    if response.status_code == 200:
        print("Authenticated successfully")
        return response.headers['x-vcloud-authorization']
    else:
        raise Exception("Failed to authenticate")

# Get a list of all VMs
def get_all_vms(session_token):
    headers = {
        'Accept': 'application/*+xml;version=34.0',
        'x-vcloud-authorization': session_token,
    }

    response = requests.get(f'{vcloud_url}/vms/query', headers=headers)
    if response.status_code == 200:
        vms_list = xmltodict.parse(response.content)
        return vms_list
    else:
        raise Exception(f"Failed to get VM list: {response.status_code}")

# Main function
if __name__ == "__main__":
    try:
        session_token = get_vcloud_session()
        vms_list = get_all_vms(session_token)
        print(vms_list)
    except Exception as e:
        print(f"Error: {e}")
