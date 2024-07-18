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
    'Accept': 'application/json;version=39.0.0-alpha',
    'Authorization': f'Bearer {auth_token}'
    }

# The JSON data
data = {
    "description": "",
    "name": "vcd-external-net",
    "networkBackings": {
        "values": [
            {
                "backingId": "c758a1d4-6110-4267-a99b-dd00439a1fc2",
                "name": "vcd-external",
                "backingType": "UNKNOWN",
                "backingTypeValue": "IMPORTED_T_LOGICAL_SWITCH",
                "networkProvider": {
                    "name": "nsxm01.ch3.lab",
                    "id": "urn:vcloud:nsxtmanager:36f31381-6003-444d-a375-5c19374510d0"
                }
            }
        ]
    },
    "subnets": {
        "values": [
            {
                "gateway": "10.30.20.1",
                "prefixLength": "24",
                "dnsSuffix": "",
                "dnsServer1": "",
                "dnsServer2": "",
                "ipRanges": {
                    "values": [
                        {
                            "startAddress": "10.30.20.10",
                            "endAddress": "10.30.20.100"
                        }
                    ]
                },
                "enabled": "true",
                "usedIpCount": "0",
                "totalIpCount": "0"
            }
        ]
    },
}

# Make the subsequent API request with SSL verification disabled
print("Creating Provider External Network")
api_createprovider = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)

# Check the response
if api_createprovider.status_code == 202:
    print("Provider External Network Created Successfully")
else:
    print("Error:", api_createprovider.status_code, api_createprovider.text)
