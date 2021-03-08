import requests
import json
from requests.auth import HTTPBasicAuth

from env import config

headers = {
    "X-Cisco-Meraki-API-Key": config['MERAKI_KEY']
}

desiredOrg = "DevNet Sandbox"
desiredNetworm = "DevNet Sandbox ALWAYS ON"
filename = "Inventory_"

# Get available organizations
orgs_url = f"{config['MERAKI_BASE_URL']}/organizations"
resp = requests.get(orgs_url, headers=headers)
parsed = json.loads(resp.text)

print("ORGANIZATIONS")
if resp.status_code == 200:
    print(json.dumps(parsed, indent=4, sort_keys=True))
else:
    print(f"Meraki status code: {resp.status_code}")

# Find organization id for specific organization
def findOrg(data):
    for entry in data:
            if desiredOrg == entry["name"]:
                print(entry["id"])
                return entry["id"]

orgId = findOrg(parsed)

# Get networks in organization
orgs_url = f"{config['MERAKI_BASE_URL']}/organizations/{orgId}/networks"
resp = requests.get(orgs_url, headers=headers)
parsed = json.loads(resp.text)

print("NETWORKS")
if resp.status_code == 200:
    print(json.dumps(parsed, indent=4, sort_keys=True))
else:
    print(f"Meraki status code: {resp.status_code}")


# Find network id for specific network
def findNetwork(data):
    for entry in data:
            if desiredNetworm == entry["name"]:
                print(entry["id"])
                return entry["id"]

networkId = findNetwork(parsed)

# Get full list of devices in network 
orgs_url = f"{config['MERAKI_BASE_URL']}/networks/{networkId}/devices"
resp = requests.get(orgs_url, headers=headers)
parsed = json.loads(resp.text)

print("DEVICES")
if resp.status_code == 200:
    print(json.dumps(parsed, indent=4, sort_keys=True))
else:
    print(f"Meraki status code: {resp.status_code}")

# Go from full output data to name:type:mac:serial dictionary
def clean(raw_data):
    clean_data = []
    for entry in raw_data:
        if "name" in entry: 
            clean_data.append({"name":entry["name"], "mac":entry["mac"], "serial":entry["serial"], "type":entry["model"]})
        else:
            name = f"Nameless {len(clean_data)}"
            clean_data.append({"name":name, "mac":entry["mac"], "serial":entry["serial"], "type":entry["model"]})
    return clean_data

inventory = clean(parsed)

print(json.dumps(inventory, indent=4, sort_keys=True))

# Write dictionary into CSV file
def write_json(data):
    with open(filename + orgId + ".json", "w") as f:
        try:
            f.write(json.dumps(inventory, indent=4, sort_keys=True))
        except:
            print("Something went wrong")
    f.close()
    print("Result written to " + filename + orgId + ".json")

write_json(inventory)