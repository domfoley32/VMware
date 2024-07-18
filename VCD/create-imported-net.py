#CREATE ORG VDC IMPORTED NETWORK

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
api_url = 'https://<VCD FQDN>/cloudapi/1.0.0/orgVdcNetworks'

# Headers for the subsequent API request
headers = {
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Accept': 'application/*',
    'Accept': 'application/json;version=39.0.0-alpha',
    'Authorization': f'Bearer {auth_token}'
    }

# The JSON data
jsondata = '''
{
    "backingNetworkId": "263ca078-f5b4-48a6-9c42-025d114f686c",
    "backingNetworkType": "IMPORTED_T_LOGICAL_SWITCH",
    "description": "",
    "enableDualSubnetNetwork": "false",
    "name": "orgvdc-imported",
    "networkType": "OPAQUE",
    "ownerRef": {
        "id": "urn:vcloud:vdc:140362ce-189f-4777-86a2-18ad77a444e5",
        "name": "OVDC.CH3.LAB"
    },
    "segmentProfileTemplateRef": null,  
    "subnets": {
        "values": [
            {
                "gateway": "50.50.50.1",
                "prefixLength": "24",
                "dnsServer1": "1.1.1.1",
                "dnsServer2": "1.1.1.2",
                "dnsSuffix": "ch3.lab",
                "ipRanges": {
                    "values": [
                        {
                            "startAddress": "50.50.50.10",
                            "endAddress": "50.50.50.100"
                        }
                    ]
                }
            }
        ]
    }    
}
'''

data = json.loads(jsondata)

# Make the subsequent API request with SSL verification disabled
print("Creating ORG VDC Imported Network")
api_createprovider = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)

# Check the response
if api_createprovider.status_code == 202:
    print("ORG VDC Imported Network Created Successfully")
else:
    print("Error:", api_createprovider.status_code, api_createprovider.text)
