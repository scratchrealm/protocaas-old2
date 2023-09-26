from typing import Union, List, Any
import time
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field
from ..common._create_random_id import _create_random_id
from ..common.protocaas_types import ProtocaasJob, ProtocaasProject, ProtocaasWorkspace
from ._authenticate_gui_request import _authenticate_gui_request
from ._get_workspace_role import _get_workspace_role


router = APIRouter()

# get project
class GetProjectReponse(BaseModel):
    project: ProtocaasProject
    success: bool

@router.get("/api/gui/projects/{project_id}")
async def get_project(project_id, request: Request):
    try:
        client = _get_mongo_client()
        projects_collection = client['protocaas']['projects']
        project = await projects_collection.find_one({'projectId': project_id})
        _remove_id_field(project)
        if project is None:
            raise Exception(f"No project with ID {project_id}")
        project = ProtocaasProject(**project) # validate project
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

@router.post("/api/gui/projects")
async def create_project(data: CreateProjectRequest, request: Request) -> CreateProjectResponse:
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        workspace_id = data.workspaceId
        name = data.name

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        _remove_id_field(workspace)
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
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
        projects_collection = client['protocaas']['projects']
        await projects_collection.insert_one(project.dict(exclude_none=True))

        await workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'timestampModified': time.time()
            }
        })

        return CreateProjectResponse(projectId=project_id, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set project name
class SetProjectNameRequest(BaseModel):
    name: str

class SetProjectNameResponse(BaseModel):
    success: bool

@router.put("/api/gui/projects/{project_id}/name")
async def set_project_name(project_id, data: SetProjectNameRequest, request: Request) -> SetProjectNameResponse:
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        name = data.name

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
            raise Exception('User does not have permission to edit projects')
        
        projects_collection.update_one({'projectId': project_id}, {
            '$set': {
                'name': name,
                'timestampModified': time.time()
            }
        })

        return SetProjectNameResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete project
class DeleteProjectResponse(BaseModel):
    success: bool

@router.delete("/api/gui/projects/{project_id}")
async def delete_project(project_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

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
        if workspace_role != 'admin':
            raise Exception('User does not have permission to delete projects')
        
        files_collection = client['protocaas']['files']
        await files_collection.delete_many({'projectId': project_id})

        jobs_collection = client['protocaas']['jobs']
        await jobs_collection.delete_many({'projectId': project_id})

        await projects_collection.delete_one({'projectId': project_id})

        workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'timestampModified': time.time()
            }
        })

        return DeleteProjectResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get jobs
class GetJobsResponse(BaseModel):
    jobs: List[ProtocaasJob]
    success: bool

@router.get("/api/gui/projects/{project_id}/jobs")
async def get_jobs(project_id, request: Request):
    try:
        client = _get_mongo_client()
        jobs_collection = client['protocaas']['jobs']
        jobs = await jobs_collection.find({
            'projectId': project_id
        }).to_list(length=None)
        for job in jobs:
            _remove_id_field(job)
        jobs = [ProtocaasJob(**job) for job in jobs] # validate jobs
        for job in jobs:
            job.jobPrivateKey = '' # hide the private key
        return GetJobsResponse(jobs=jobs, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))