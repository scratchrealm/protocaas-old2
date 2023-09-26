import os
from pydantic import BaseModel
from fastapi import APIRouter, Request
import aiohttp


router = APIRouter()

# github auth
class GithubAuthResponse(BaseModel):
    access_token: str

@router.get("/github_auth/{code}")
async def github_auth(code, request: Request) -> GithubAuthResponse:
    GITHUB_CLIENT_ID = os.environ.get('VITE_GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
    if GITHUB_CLIENT_ID is None:
        raise Exception('Env var not set: VITE_GITHUB_CLIENT_ID')
    if GITHUB_CLIENT_SECRET is None:
        raise Exception('Env var not set: GITHUB_CLIENT_SECRET')
    url = f'https://github.com/login/oauth/access_token?client_id=${GITHUB_CLIENT_ID}&client_secret=${GITHUB_CLIENT_SECRET}&code=${code}'
    headers = {
        'accept': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            r = await resp.json()
            if 'access_token' not in r:
                raise Exception(f'No access_token in response: {r["error"]} ({r["error_description"]})')
            return GithubAuthResponse(access_token=r['access_token'])