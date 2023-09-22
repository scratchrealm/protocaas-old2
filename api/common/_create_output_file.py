import aiohttp
from ._get_mongo_client import _get_mongo_client
from ._set_file import _set_file


async def _create_output_file(*,
    file_name: str,
    url: str,
    workspace_id: str,
    project_id: str,
    user_id: str,
    job_id: str
) -> str: # returns the ID of the created file
    size = await _get_size_for_remote_file(url)

    await _set_file(
        project_id=project_id,
        workspace_id=workspace_id,
        file_name=file_name,
        content=f"url:{url}",
        size=size,
        job_id=job_id,
        user_id=user_id,
        metadata={}
    )

    client = _get_mongo_client()
    files_collection = client['protocaas']['files']
    file = await files_collection.find_one({
        'projectId': project_id,
        'fileName': file_name
    })
    if file is None:
        raise Exception('Unexpected: File not found in database')
    return file['fileId']

async def _get_size_for_remote_file(url: str) -> int:
    response = await _head_request(url)
    if response is None:
        raise Exception(f"Unable to HEAD {url}")
    size = int(response.headers.get('content-length'))
    if size is None:
        raise Exception(f"Unable to get content-length for {url}")
    return size

async def _head_request(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as response:
            return response