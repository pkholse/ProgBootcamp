import requests
import json
from requests.auth import HTTPBasicAuth

from env import config

headers = {
    "X-Cisco-Meraki-API-Key": config['MERAKI_KEY']
}

desiredOrg = "DevNet Sandbox"
desiredNetwork = "DevNet Sandbox ALWAYS ON"
filename = "Inventory_"
dnac_token = ""

# Get available organizations
def getOrgs():
    orgs_url = f"{config['MERAKI_BASE_URL']}/organizations"
    resp = requests.get(orgs_url, headers=headers)
    parsed = json.loads(resp.text)

    print("ORGANIZATIONS")
    if resp.status_code == 200:
        #print(json.dumps(parsed, indent=4, sort_keys=True))
        print("Meraki organisations succesfully collected")
    else:
        print(f"Meraki status code: {resp.status_code}")
    return parsed

# Find organization id for specific organization
def findOrgId(data, theOrg):
    for entry in data:
            if theOrg == entry["name"]:
                return entry["id"]

# Get networks in organization
def getNetworks(orgId):
    orgs_url = f"{config['MERAKI_BASE_URL']}/organizations/{orgId}/networks"
    resp = requests.get(orgs_url, headers=headers)
    parsed = json.loads(resp.text)

    if resp.status_code == 200:
        print("Meraki networks succesfully collected")
    else:
        print(f"Meraki status code: {resp.status_code}")

    return parsed

# Find network id for specific network
def findNetworkId(data, theNetwork):
    for entry in data:
            if theNetwork == entry["name"]:
                return entry["id"]

# Get full list of devices in network 
def getDevices(networkId):
    orgs_url = f"{config['MERAKI_BASE_URL']}/networks/{networkId}/devices"
    resp = requests.get(orgs_url, headers=headers)
    parsed = json.loads(resp.text)

    if resp.status_code == 200:
        print("Meraki devices succesfully collected")
    else:
        print(f"Meraki status code: {resp.status_code}")
    return parsed

# Go from full output data to name:type:mac:serial dictionary
def clean(raw_data):
    clean_data = []
    for device in raw_data:
        new_device = {"category": "Meraki"}
        if "name" in device: 
                new_device["name"] = device["name"]
        if "mac" in device: 
                new_device["mac"] = device["mac"]
        if "serial" in device: 
                new_device["serial"] = device["serial"]
        if "type" in device: 
                new_device["type"] = device["type"]
        clean_data += [new_device]
    return clean_data

# Get DNAC access token
def dnacAccess():
    dnac_auth_url = f"{config['DNAC_BASE_URL']}/dna/system/api/v1/auth/token"

    resp = requests.post(dnac_auth_url, auth=HTTPBasicAuth(config['DNAC_USER'], config['DNAC_PASSWORD']))
    parsed = json.loads(resp.text)

    if resp.status_code == 200:
        print("DNAC Access verified")
        #print(json.dumps(parsed, indent=4, sort_keys=True))
    else:
        print(f"DNAC status code: {resp.status_code}")

    return parsed["Token"]

# Get full list of devices in network 
def getDnacDevices():
    dnac_url = f"{config['DNAC_BASE_URL']}/dna/intent/api/v1/network-device"
    dnac_header = {"x-auth-token": dnac_token}

    resp = requests.get(dnac_url, headers=dnac_header)
    parsed = json.loads(resp.text)

    if resp.status_code == 200:
        print("DNAC devices succesfully collected")
        #print(json.dumps(parsed, indent=4, sort_keys=True))
    else:
        print(f"DNAC status code: {resp.status_code}")

    return parsed

# Go from full output data to name:type:mac:serial dictionary
def clean_DNAC(raw_data):
    clean_data = []
    for device in raw_data["response"]:
        new_device = {"category": "DNA Center"}
        if "hostname" in device: 
                new_device["name"] = device["hostname"]
        if "macAddress" in device: 
                new_device["mac"] = device["macAddress"]
        if "serialNumber" in device: 
                new_device["serial"] = device["serialNumber"]
        if "platformId" in device: 
                new_device["type"] = device["platformId"]
        clean_data += [new_device]
    return clean_data

# Write dictionary into CSV file
def write_json(data):
    with open(filename + ".json", "w") as f:
        try:
            f.write(json.dumps(inventory, indent=4, sort_keys=True))
        except:
            print("Something went wrong")
    f.close()
    print("Result written to " + filename + orgId + ".json")


# MAIN
orgList = getOrgs()
orgId = findOrgId(orgList,desiredOrg)
networkList = getNetworks(orgId)
networkId = findNetworkId(networkList, desiredNetwork)
devices = getDevices(networkId)
merakiInventory = clean(devices)

dnac_token = dnacAccess()
dnacDevices = getDnacDevices()
dnacInventory = clean_DNAC(dnacDevices)

inventory = merakiInventory + dnacInventory
write_json(inventory)
