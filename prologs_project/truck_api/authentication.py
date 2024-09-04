import requests

def get_access_token():
    url = 'https://identity-stage.prologs.us/connect/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': '9595d560-b813-4cd8-a03a-49b3e28c2dc6',
        'client_secret': 'uBPCTWyQ9DJT2w6dER6kwXfjNcZJgvOj'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=data, headers=headers)
    response_data = response.json()
    return response_data['access_token']

import requests
from .authentication import get_access_token

def fetch_api_data(endpoint):
    token = get_access_token()
    url = f'https://publicapi-stage.prologs.us/api/v1/{endpoint}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    return response.json()
