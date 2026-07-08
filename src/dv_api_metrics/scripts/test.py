import requests
import logging
import os
from dotenv import load_dotenv

#api_token = "df352504-8440-4f99-bbbe-c0ecfdda6f69"
server_url = "https://dataverse.harvard.edu"
persistent_id = "doi:10.7910/DVN/TMWYHB"  # This one worked in curl
metadata_format = "ddi"


load_dotenv('/Users/alliej/Desktop/bu/CAFE/use_api/dv-api-metrics/.env')

api_token = os.getenv('DATAVERSE_API_TOKEN')
if not api_token:
    raise Exception('Environment variable: "DATAVERSE_API_TOKEN" is not set')
logging.info(f'Token loaded: {api_token[:20]}...')  # Show first 20 chars
logging.info(f'Token length: {len(api_token)}')
logging.info(f'Token repr: {repr(api_token)}')
logging.info(f'Token starts with: {repr(api_token[:10])}')
logging.info(f'Token ends with: {repr(api_token[-10:])}')


url = f"{server_url}/api/datasets/export"
headers = {'X-Dataverse-key': api_token}
params = {
    'exporter': metadata_format,
    'persistentId': persistent_id,
    'version': ':latest-published'
}

response = requests.get(url, headers=headers, params=params, timeout=30)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✓ SUCCESS")
    print(response.text[:200])
else:
    print(f"✗ FAILED: {response.status_code}")
    print(response.text)