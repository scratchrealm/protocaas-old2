from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field
from ..common._remove_detached_files_and_jobs import _remove_detached_files_and_jobs
from ..common._set_file import _set_file
from ._authenticate_gui_request import _authenticate_gui_request
from ._get_workspace_role import _get_workspace_role


router = APIRouter()

# get file
@router.get("/api/gui/projects/{project_id}/files/{file_name:path}")
async def get_file(project_id, file_name, request: Request):
    try:
        client = _get_mongo_client()
        files_collection = client['protocaas']['files']
        file = await files_collection.find_one({
            'projectId': project_id,
            'fileName': file_name
        })
        _remove_id_field(file)
        if file is None:
            raise Exception(f"No file with name {file_name} in project with ID {project_id}")
        return {'file': file, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get files
@router.get("/api/gui/projects/{project_id}/files")
async def get_files(project_id, request: Request):
    try:
        client = _get_mongo_client()
        files_collection = client['protocaas']['files']
        files = await files_collection.find({
            'projectId': project_id
        }).to_list(length=None)
        for file in files:
            _remove_id_field(file)
        return {'files': files, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set file
@router.put("/api/gui/projects/{project_id}/files/{file_name}")
async def set_file(project_id, file_name, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        body = await request.json()
        content = body['content']
        job_id = body.get('jobId', None)
        size = body.get('size', None)
        metadata = body.get('metadata', {})

        client = _get_mongo_client()
        projects_collection = client['protocaas']['projects']
        project = await projects_collection.find_one({'projectId': project_id})
        if project is None:
            raise Exception(f"No project with ID {project_id}")
        workspace_id = project['workspaceId']
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to set file content in this project')

        file_id = await _set_file(
            project_id=project_id,
            workspace_id=workspace_id,
            file_name=file_name,
            content=content,
            size=size,
            job_id=job_id,
            metadata=metadata
        )

        return {'fileId': file_id, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete file
@router.delete("/api/gui/projects/{project_id}/files/{file_name}")
async def delete_file(project_id, file_name, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        files_collection = client['protocaas']['files']
        file = await files_collection.find_one({
            'projectId': project_id,
            'fileName': file_name
        })
        if file is None:
            raise Exception(f"No file with name {file_name} in project with ID {project_id}")
        workspace_id = file['workspaceId']
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to delete files in this project')

        files_collection.delete_one({
            'projectId': project_id,
            'fileName': file_name
        })

        # remove detached files and jobs
        await _remove_detached_files_and_jobs(project_id)

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))