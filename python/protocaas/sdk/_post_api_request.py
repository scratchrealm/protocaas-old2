import os
import requests


def _post_api_request(req):
    """Post a request to the protocaas API"""
    protocaas_url = os.environ.get('PROTOCAAS_URL', 'https://protocaas.vercel.app')
    resp = requests.post(f'{protocaas_url}/api/protocaas', json=req)
    if resp.status_code != 200:
        msg = resp.text
        raise ValueError(f'Error posting protocaas request: {msg}')
    return resp.json()