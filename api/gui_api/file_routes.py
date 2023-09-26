from typing import Union, List, Any
import time
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field
from ..common._remove_detached_files_and_jobs import _remove_detached_files_and_jobs
from ..common._create_random_id import _create_random_id
from ..common.protocaas_types import ProtocaasFile, ProtocaasProject, ProtocaasWorkspace
from ._authenticate_gui_request import _authenticate_gui_request
from ._get_workspace_role import _get_workspace_role


router = APIRouter()

# get file
class GetFileResponse(BaseModel):
    file: ProtocaasFile
    success: bool

@router.get("/api/gui/projects/{project_id}/files/{file_name:path}")
async def get_file(project_id, file_name, request: Request):
    try:
        client = _get_mongo_client()
        files_collection = client['protocaas']['files']
        file = await files_collection.find_one({
            'projectId': project_id,
            'fileName': file_name
        })
        if file is None:
            raise Exception(f"No file with name {file_name} in project with ID {project_id}")
        _remove_id_field(file)
        file = ProtocaasFile(**file) # validate file
        return {'file': file, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get files
class GetFilesResponse(BaseModel):
    files: List[ProtocaasFile]
    success: bool

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
        files = [ProtocaasFile(**file) for file in files] # validate files
        return {'files': files, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set file
class SetFileRequest(BaseModel):
    content: str
    jobId: Union[str, None] = None
    size: Union[int, None] = None
    metadata: dict = {}

class SetFileResponse(BaseModel):
    fileId: str
    success: bool

@router.put("/api/gui/projects/{project_id}/files/{file_name:path}")
async def set_file(project_id, file_name, data: SetFileRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        content = data.content
        job_id = data.jobId
        size = data.size
        metadata = data.metadata

        client = _get_mongo_client()
        projects_collection = client['protocaas']['projects']
        project = await projects_collection.find_one({'projectId': project_id})
        if project is None:
            raise Exception(f"No project with ID {project_id}")
        _remove_id_field(project)
        project = ProtocaasProject(**project) # validate project
        workspace_id = project.workspaceId
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        _remove_id_field(workspace)
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to set file content in this project')

        files_collection = client['protocaas']['files']  
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

        new_file = ProtocaasFile(
            projectId=project_id,
            workspaceId=workspace_id,
            fileId=_create_random_id(8),
            userId=user_id,
            fileName=file_name,
            size=size,
            timestampCreated=time.time(),
            content=content,
            metadata=metadata,
            jobId=job_id
        )
        await files_collection.insert_one(new_file.dict(exclude_none=True))

        if deleted_old_file:
            await _remove_detached_files_and_jobs(project_id)
        
        await projects_collection.update_one({
            'projectId': project_id
        }, {
            '$set': {
                'timestampModified': time.time()
            }
        })

        return SetFileResponse(fileId=new_file.fileId, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete file
class DeleteFileResponse(BaseModel):
    success: bool

@router.delete("/api/gui/projects/{project_id}/files/{file_name:path}")
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
        _remove_id_field(workspace)
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to delete files in this project')

        files_collection.delete_one({
            'projectId': project_id,
            'fileName': file_name
        })

        # remove detached files and jobs
        await _remove_detached_files_and_jobs(project_id)

        return DeleteFileResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))