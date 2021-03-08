import requests
import json
from requests.auth import HTTPBasicAuth

from env import config


# Verify Meraki access
headers = {
    "X-Cisco-Meraki-API-Key": config['MERAKI_KEY']
}

orgs_url = f"{config['MERAKI_BASE_URL']}/organizations"
resp = requests.get(orgs_url, headers=headers)


if resp.status_code == 200:
    parsed = json.loads(resp.text)
    print(json.dumps(parsed, indent=4, sort_keys=True))
else:
    print(f"Meraki status code: {resp.status_code}")