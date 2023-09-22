import time
from ._get_mongo_client import _get_mongo_client
from ._remove_detached_files_and_jobs import _remove_detached_files_and_jobs


async def _set_file(*,
    project_id: str,
    workspace_id: str,
    file_name: str,
    content: str,
    size: int,
    job_id: str,
    user_id: str,
    metadata: dict
):
    client = _get_mongo_client()
    projects_collection = client['protocaas']['projects']
    files_collection = client['protocaas']['files']

    project = await projects_collection.find_one({
        'projectId': project_id
    })
    if project is None:
        raise Exception('Project not found')
    if project['workspaceId'] != workspace_id:
        raise Exception('Incorrect workspace ID')
    
    existing_file = await files_collection.find_one({
        'projectId': project_id,
        'fileName': file_name
    })
    if existing_file is not None:
        await files_collection.delete_one({
            'projectId': project_id,
            'fileName': file_name
        })
        deleted_old_file = True
    else:
        deleted_old_file = False

    new_file = {
        'projectId': project_id,
        'workspaceId': workspace_id,
        'fileId': _create_random_id(8),
        'userId': user_id,
        'fileName': file_name,
        'size': size,
        'timestampCreated': time.time(),
        'content': content,
        'metadata': metadata
    }
    if job_id is not None:
        new_file['jobId'] = job_id
    await files_collection.insert_one(new_file)

    if deleted_old_file:
        await _remove_detached_files_and_jobs(project_id)
    
    await projects_collection.update_one({
        'projectId': project_id
    }, {
        '$set': {
            'timestampModified': time.time()
        }
    })

    workspaces_collection = client['protocaas']['workspaces']
    await workspaces_collection.update_one({
        'workspaceId': workspace_id
    }, {
        '$set': {
            'timestampModified': time.time()
        }
    })

    return new_file['fileId']

def _create_random_id(length: int) -> str:
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))