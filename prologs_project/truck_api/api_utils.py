import requests
from .authentication import get_access_token

def fetch_api_data(endpoint):
    token = get_access_token()
    url = f'https://publicapi-stage.prologs.us/api/v1/{endpoint}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    return response.json()
