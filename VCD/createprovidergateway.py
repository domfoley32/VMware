import json 
import requests
from requests.auth import HTTPBasicAuth

# Credentials and vCloud Director URL
username = 'administrator@system'
password = '<PASSWORD>'
vcloud_url = 'https://<VCD FQDN>/cloudapi/1.0.0/sessions/provider'

headers1 = {
    'Accept': 'application/json;version=38.1',
    'Content-Type': 'application/json',
}

# Disable SSL warnings (optional)
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Authenticate to vCloud Director
auth_response = requests.post(vcloud_url, auth=HTTPBasicAuth(f'{username}', password), headers=headers1, verify=False)

# Check the authentication response
if auth_response.status_code == 200:
    print("Authenticated successfully")
    # Extract the token from the response headers
    auth_token = auth_response.headers['X-VMWARE-VCLOUD-ACCESS-TOKEN']
    print("Authorization Token:", auth_token)
else:
    print("Failed to authenticate", auth_response.status_code, auth_response.text)
    exit()

# URL of the API endpoint for subsequent request
api_url = 'https://<VCD FQDN>/cloudapi/1.0.0/externalNetworks'

# Headers for the subsequent API request
headers = {
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Accept': 'application/*',
    'Accept': 'application/json;version=38.1',
    'Authorization': f'Bearer {auth_token}'
    }

# The JSON data
data = {
  "dedicatedOrg": {
    "id": "urn:vcloud:org:a69ecf05-7ec5-46d1-8ad5-e831b30ba48c",
    "name": "ORG.CH3.LAB"
  },
  "description": "My VRF",
  "name": "VRF-Gateway",
  "networkBackings": {
    "values": [
      {
        "backingId": "82454608-efe6-48a7-bfbc-dcade7284b06",    <<<< This is the NSX Object ID of the Tier0 VRF Gateway
        "name": "orgvdc-vrf.ch3.lab",
        "backingType": "NSXT_TIER0",
        "backingTypeValue": "NSXT_TIER0",
        "networkProvider": {
          "name": "nsxm01.ch3.lab",
          "id": "urn:vcloud:nsxtmanager:36f31381-6003-444d-a375-5c19374510d0"
        }
      }
    ]
  },
  "subnets": {
    "values": []
  },
  "usingIpSpace": "True"
}

# Make the subsequent API request with SSL verification disabled
print("Creating Provider Gateway")
api_createprovider = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)

# Check the response
if api_createprovider.status_code == 202:
    print("Provider Gateway Created Successfully")
else:
    print("Error:", api_createprovider.status_code, api_createprovider.text)
