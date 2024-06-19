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

# Get VM information
def get_vm_info(session_token, vm_id):
    headers = {
        'Accept': 'application/*+xml;version=34.0',
        'x-vcloud-authorization': session_token,
    }

    response = requests.get(f'{vcloud_url}/vApp/vm-{vm_id}', headers=headers)
    if response.status_code == 200:
        vm_info = xmltodict.parse(response.content)
        return vm_info
    else:
        raise Exception(f"Failed to get VM info: {response.status_code}")

# Main function
if __name__ == "__main__":
    try:
        session_token = get_vcloud_session()
        vm_id = "your-vm-id"  # Replace with your VM ID
        vm_info = get_vm_info(session_token, vm_id)
        print(vm_info)
    except Exception as e:
        print(f"Error: {e}")


