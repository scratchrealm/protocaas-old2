from typing import List
import time
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from ...core._create_random_id import _create_random_id
from ...core.protocaas_types import ProtocaasJob, ProtocaasProject
from ._authenticate_gui_request import _authenticate_gui_request
from ...core._get_workspace_role import _get_workspace_role
from ...clients.db import fetch_project, fetch_workspace, insert_project, update_workspace, update_project, fetch_project_jobs
from ...services.gui.delete_project import delete_project as service_delete_project


router = APIRouter()

# get project
class GetProjectReponse(BaseModel):
    project: ProtocaasProject
    success: bool

@router.get("/{project_id}")
async def get_project(project_id):
    try:
        project = await fetch_project(project_id)
        if project is None:
            raise Exception(f"No project with ID {project_id}")
        return GetProjectReponse(project=project, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# create project
class CreateProjectRequest(BaseModel):
    workspaceId: str
    name: str

class CreateProjectResponse(BaseModel):
    projectId: str
    success: bool

@router.post("")
async def create_project(data: CreateProjectRequest, github_access_token: str=Header(...)) -> CreateProjectResponse:
    try:
        # authenticate the request
        user_id = await _authenticate_gui_request(github_access_token)
        if not user_id:
            raise Exception('User is not authenticated')

        # parse the request
        workspace_id = data.workspaceId
        name = data.name

        workspace = await fetch_workspace(workspace_id)
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to create projects')
        
        project_id = _create_random_id(8)
        project = ProtocaasProject(
            projectId=project_id,
            workspaceId=workspace_id,
            name=name,
            description='',
            timestampCreated=time.time(),
            timestampModified=time.time()
        )

        await insert_project(project)
        
        await update_workspace(workspace_id, update={
            'timestampModified': time.time()
        })

        return CreateProjectResponse(projectId=project_id, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set project name
class SetProjectNameRequest(BaseModel):
    name: str

class SetProjectNameResponse(BaseModel):
    success: bool

@router.put("/{project_id}/name")
async def set_project_name(project_id, data: SetProjectNameRequest, github_access_token: str=Header(...)) -> SetProjectNameResponse:
    try:
        # authenticate the request
        user_id = await _authenticate_gui_request(github_access_token)
        if not user_id:
            raise Exception('User is not authenticated')
        
        project = await fetch_project(project_id)
        if project is None:
            raise Exception(f"No project with ID {project_id}")

        workspace_id = project.workspaceId
        workspace = await fetch_workspace(workspace_id)
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to set project names')

        # parse the request
        name = data.name

        await update_project(project_id, update={
            'name': name,
            'timestampModified': time.time()
        })

        await update_workspace(workspace_id, update={
            'timestampModified': time.time()
        })

        return SetProjectNameResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete project
class DeleteProjectResponse(BaseModel):
    success: bool

@router.delete("/{project_id}")
async def delete_project(project_id, github_access_token: str=Header(...)) -> DeleteProjectResponse:
    try:
        # authenticate the request
        user_id = await _authenticate_gui_request(github_access_token)
        if not user_id:
            raise Exception('User is not authenticated')
        
        project = await fetch_project(project_id)
        if project is None:
            raise Exception(f"No project with ID {project_id}")
        
        workspace_id = project.workspaceId
        workspace = await fetch_workspace(workspace_id)
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to delete projects')
        
        await service_delete_project(project)
        
        return DeleteProjectResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get jobs
class GetJobsResponse(BaseModel):
    jobs: List[ProtocaasJob]
    success: bool

@router.get("/{project_id}/jobs")
async def get_jobs(project_id):
    try:
        jobs = await fetch_project_jobs(project_id, include_private_keys=False)
        return GetJobsResponse(jobs=jobs, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))