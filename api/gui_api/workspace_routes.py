from typing import Union, List, Any
import time
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field
from ..common._create_random_id import _create_random_id
from ..common.protocaas_types import ProtocaasWorkspace, ProtocaasWorkspaceUser, ProtocaasProject
from ._authenticate_gui_request import _authenticate_gui_request
from ._get_workspace_role import _get_workspace_role


router = APIRouter()

# create workspace
class CreateWorkspaceRequest(BaseModel):
    name: str

class CreateWorkspaceResponse(BaseModel):
    workspaceId: str
    success: bool

@router.post("/api/gui/workspaces")
async def create_workspace(data: CreateWorkspaceRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if not user_id:
            raise Exception('Unexpected: no user ID')

        # parse the request
        name = data.name

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace_id = _create_random_id(8)
        workspace = ProtocaasWorkspace(
            workspaceId=workspace_id,
            ownerId=user_id,
            name=name,
            description='',
            users=[],
            publiclyReadable=True,
            listed=False,
            timestampCreated=time.time(),
            timestampModified=time.time()
        )
        await workspaces_collection.insert_one(workspace.dict(exclude_none=True))

        return CreateWorkspaceResponse(workspaceId=workspace_id, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get workspace
class GetWorkspaceResponse(BaseModel):
    workspace: ProtocaasWorkspace
    success: bool

@router.get("/api/gui/workspaces/{workspace_id}")
async def get_workspace(workspace_id, request: Request):
    try:
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        _remove_id_field(workspace)
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
        role = _get_workspace_role(workspace, user_id)
        if role == 'none':
            raise Exception('User does not have permission to read this workspace')
        return GetWorkspaceResponse(workspace=workspace, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get workspaces
class GetWorkspacesResponse(BaseModel):
    workspaces: List[ProtocaasWorkspace]
    success: bool

@router.get("/api/gui/workspaces")
async def get_workspaces(request: Request):
    try:
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspaces = await workspaces_collection.find({}).to_list(length=None)
        for workspace in workspaces:
            _remove_id_field(workspace)
        workspacces = [ProtocaasWorkspace(**workspace) for workspace in workspaces] # validate workspaces
        workspaces2: List[ProtocaasWorkspace] = []
        for workspace in workspaces:
            role = _get_workspace_role(workspace, user_id)
            if role != 'none':
                workspaces2.append(workspace)
        return GetWorkspacesResponse(workspaces=workspaces2, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set workspace name
class SetWorkspaceNameRequest(BaseModel):
    name: str

class SetWorkspaceNameResponse(BaseModel):
    success: bool

@router.put("/api/gui/workspaces/{workspace_id}/name")
async def set_workspace_name(workspace_id, data: SetWorkspaceNameRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        name = data.name

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        _remove_id_field(workspace)
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
        role = _get_workspace_role(workspace, user_id)
        if role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'name': name,
                'timestampModified': time.time()
            }
        })

        return SetWorkspaceNameResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set workspace publicly readable
class SetWorkspacePubliclyReadableRequest(BaseModel):
    publiclyReadable: bool

class SetWorkspacePubliclyReadableResponse(BaseModel):
    success: bool

@router.put("/api/gui/workspaces/{workspace_id}/publicly_readable")
async def set_workspace_public(workspace_id, data: SetWorkspacePubliclyReadableRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        publicly_readable = data.publiclyReadable

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        _remove_id_field(workspace)
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
        role = _get_workspace_role(workspace, user_id)
        if role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'publiclyReadable': publicly_readable,
                'timestampModified': time.time()
            }
        })

        return SetWorkspacePubliclyReadableResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# set workspace listed
class SetWorkspaceListedRequest(BaseModel):
    listed: bool

class SetWorkspaceListedResponse(BaseModel):
    success: bool

@router.put("/api/gui/workspaces/{workspace_id}/listed")
async def set_workspace_listed(workspace_id, data: SetWorkspaceListedRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        listed = data.listed

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        _remove_id_field(workspace)
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
        role = _get_workspace_role(workspace, user_id)
        if role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'listed': listed,
                'timestampModified': time.time()
            }
        })

        return SetWorkspaceListedResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set workspace compute resource id
class SetWorkspaceComputeResourceIdRequest(BaseModel):
    computeResourceId: str

class SetWorkspaceComputeResourceIdResponse(BaseModel):
    success: bool

@router.put("/api/gui/workspaces/{workspace_id}/compute_resource_id")
async def set_workspace_compute_resource_id(workspace_id, data: SetWorkspaceComputeResourceIdRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        compute_resource_id = data.computeResourceId

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        _remove_id_field(workspace)
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
        role = _get_workspace_role(workspace, user_id)
        if role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'computeResourceId': compute_resource_id,
                'timestampModified': time.time()
            }
        })

        return SetWorkspaceComputeResourceIdResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set workspace users
class SetWorkspaceUsersRequest(BaseModel):
    users: List[ProtocaasWorkspaceUser]

class SetWorkspaceUsersResponse(BaseModel):
    success: bool

@router.put("/api/gui/workspaces/{workspace_id}/users")
async def set_workspace_users(workspace_id, data: SetWorkspaceUsersRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        users = data.users

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        _remove_id_field(workspace)
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
        role = _get_workspace_role(workspace, user_id)
        if role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'users': users,
                'timestampModified': time.time()
            }
        })

        return SetWorkspaceUsersResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete workspace
class DeleteWorkspaceResponse(BaseModel):
    success: bool

@router.delete("/api/gui/workspaces/{workspace_id}")
async def delete_workspace(workspace_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()

        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        _remove_id_field(workspace)
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin':
            raise Exception('User does not have permission to delete this workspace')
        
        files_collection = client['protocaas']['files']
        await files_collection.delete_many({'workspaceId': workspace_id})

        jobs_collection = client['protocaas']['jobs']
        await jobs_collection.delete_many({'workspaceId': workspace_id})

        projects_collection = client['protocaas']['projects']
        await projects_collection.delete_many({'workspaceId': workspace_id})

        await workspaces_collection.delete_one({'workspaceId': workspace_id})

        return DeleteWorkspaceResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get projects
class GetProjectsResponse(BaseModel):
    projects: List[ProtocaasProject]
    success: bool

@router.get("/api/gui/workspaces/{workspace_id}/projects")
async def get_workspace_projects(workspace_id, request: Request):
    try:
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        _remove_id_field(workspace)
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
        role = _get_workspace_role(workspace, user_id)
        if role == 'none':
            raise Exception('User does not have permission to read this workspace')

        projects_collection = client['protocaas']['projects']
        projects = await projects_collection.find({'workspaceId': workspace_id}).to_list(length=None)
        for project in projects:
            _remove_id_field(project)
        projects = [ProtocaasProject(**project) for project in projects] # validate projects
        return GetProjectsResponse(projects=projects, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))