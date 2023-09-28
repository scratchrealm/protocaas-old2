from typing import List
import time
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from ...core.protocaas_types import ProtocaasWorkspace, ProtocaasWorkspaceUser, ProtocaasProject
from ._authenticate_gui_request import _authenticate_gui_request
from ...core._get_workspace_role import _get_workspace_role
from ...services.gui.create_workspace import create_workspace as service_create_workspace
from ...services.gui.delete_workspace import delete_workspace as service_delete_workspace
from ...clients.db import fetch_workspace, fetch_workspaces_for_user, update_workspace, fetch_projects_in_workspace


router = APIRouter()

# create workspace
class CreateWorkspaceRequest(BaseModel):
    name: str

class CreateWorkspaceResponse(BaseModel):
    workspaceId: str
    success: bool

@router.post("")
async def create_workspace(data: CreateWorkspaceRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if not user_id:
            raise Exception('User is not authenticated')

        # parse the request
        name = data.name

        workspace_id = await service_create_workspace(name=name, user_id=user_id)

        return CreateWorkspaceResponse(workspaceId=workspace_id, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get workspace
class GetWorkspaceResponse(BaseModel):
    workspace: ProtocaasWorkspace
    success: bool

@router.get("/{workspace_id}")
async def get_workspace(workspace_id, request: Request):
    try:
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        workspace = await fetch_workspace(workspace_id)
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role == 'none':
            raise Exception('User does not have permission to read this workspace')

        return GetWorkspaceResponse(workspace=workspace, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get workspaces
class GetWorkspacesResponse(BaseModel):
    workspaces: List[ProtocaasWorkspace]
    success: bool

@router.get("")
async def get_workspaces(request: Request):
    try:
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        workspaces = await fetch_workspaces_for_user(user_id)

        return GetWorkspacesResponse(workspaces=workspaces, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set workspace name
class SetWorkspaceNameRequest(BaseModel):
    name: str

class SetWorkspaceNameResponse(BaseModel):
    success: bool

@router.put("/{workspace_id}/name")
async def set_workspace_name(workspace_id, data: SetWorkspaceNameRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if not user_id:
            raise Exception('User is not authenticated')
        
        workspace = await fetch_workspace(workspace_id)
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        # parse the request
        name = data.name

        await update_workspace(workspace_id, update={
            'name': name,
            'timestampModified': time.time()
        })

        return SetWorkspaceNameResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set workspace publicly readable
class SetWorkspacePubliclyReadableRequest(BaseModel):
    publiclyReadable: bool

class SetWorkspacePubliclyReadableResponse(BaseModel):
    success: bool

@router.put("/{workspace_id}/publicly_readable")
async def set_workspace_public(workspace_id, data: SetWorkspacePubliclyReadableRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if not user_id:
            raise Exception('User is not authenticated')
        
        workspace = await fetch_workspace(workspace_id)
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        # parse the request
        publicly_readable = data.publiclyReadable

        await update_workspace(workspace_id, update={
            'publiclyReadable': publicly_readable,
            'timestampModified': time.time()
        })

        return SetWorkspacePubliclyReadableResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# set workspace listed
class SetWorkspaceListedRequest(BaseModel):
    listed: bool

class SetWorkspaceListedResponse(BaseModel):
    success: bool

@router.put("/{workspace_id}/listed")
async def set_workspace_listed(workspace_id, data: SetWorkspaceListedRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if not user_id:
            raise Exception('User is not authenticated')
        
        workspace = await fetch_workspace(workspace_id)
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        # parse the request
        listed = data.listed

        await update_workspace(workspace_id, update={
            'listed': listed,
            'timestampModified': time.time()
        })

        return SetWorkspaceListedResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set workspace compute resource id
class SetWorkspaceComputeResourceIdRequest(BaseModel):
    computeResourceId: str

class SetWorkspaceComputeResourceIdResponse(BaseModel):
    success: bool

@router.put("/{workspace_id}/compute_resource_id")
async def set_workspace_compute_resource_id(workspace_id, data: SetWorkspaceComputeResourceIdRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if not user_id:
            raise Exception('User is not authenticated')
        
        workspace = await fetch_workspace(workspace_id)
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        # parse the request
        compute_resource_id = data.computeResourceId

        await update_workspace(workspace_id, update={
            'computeResourceId': compute_resource_id,
            'timestampModified': time.time()
        })

        return SetWorkspaceComputeResourceIdResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set workspace users
class SetWorkspaceUsersRequest(BaseModel):
    users: List[ProtocaasWorkspaceUser]

class SetWorkspaceUsersResponse(BaseModel):
    success: bool

@router.put("/{workspace_id}/users")
async def set_workspace_users(workspace_id, data: SetWorkspaceUsersRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if not user_id:
            raise Exception('User is not authenticated')
        
        workspace = await fetch_workspace(workspace_id)
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        # parse the request
        users = data.users

        await update_workspace(workspace_id, update={
            'users': users,
            'timestampModified': time.time()
        })

        return SetWorkspaceUsersResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete workspace
class DeleteWorkspaceResponse(BaseModel):
    success: bool

@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if not user_id:
            raise Exception('User is not authenticated')
        
        workspace = await fetch_workspace(workspace_id)
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin':
            raise Exception('User does not have permission to delete this workspace')
        
        await service_delete_workspace(workspace)

        return DeleteWorkspaceResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get projects
class GetProjectsResponse(BaseModel):
    projects: List[ProtocaasProject]
    success: bool

@router.get("/{workspace_id}/projects")
async def get_workspace_projects(workspace_id, request: Request):
    try:
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        workspace = await fetch_workspace(workspace_id)
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role == 'none':
            raise Exception('User does not have permission to read this workspace')
        
        projects = await fetch_projects_in_workspace(workspace_id)

        return GetProjectsResponse(projects=projects, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))