from typing import Union, List, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field
from ..common.protocaas_types import ProtocaasProject, ProtocaasFile, ProtocaasJob

router = APIRouter()

# get project
class GetProjectResponse(BaseModel):
    project: ProtocaasProject
    success: bool

@router.get("/api/client/projects/{project_id}")
async def get_project(project_id, request: Request) -> GetProjectResponse:
    try:
        client = _get_mongo_client()
        projects_collection = client['protocaas']['projects']
        project = await projects_collection.find_one({'projectId': project_id})
        # here I'd like to validate project
        _remove_id_field(project)
        if project is None:
            raise Exception(f"No project with ID {project_id}")
        project = ProtocaasProject(**project) # validate project
        return GetProjectResponse(project=project, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get project files
class GetProjectFilesResponse(BaseModel):
    files: List[ProtocaasFile]
    success: bool

@router.get("/api/client/projects/{project_id}/files")
async def get_project_files(project_id, request: Request) -> GetProjectFilesResponse:
    try:
        client = _get_mongo_client()
        files_collection = client['protocaas']['files']
        files = await files_collection.find({'projectId': project_id}).to_list(length=None)
        for file in files:
            _remove_id_field(file)
        files = [ProtocaasFile(**file) for file in files] # validate files
        return GetProjectFilesResponse(files=files, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get project jobs
class GetProjectJobsResponse(BaseModel):
    jobs: List[ProtocaasJob]
    success: bool

@router.get("/api/client/projects/{project_id}/jobs")
async def get_project_jobs(project_id, request: Request) -> GetProjectJobsResponse:
    try:
        client = _get_mongo_client()
        jobs_collection = client['protocaas']['jobs']
        jobs = await jobs_collection.find({'projectId': project_id}).to_list(length=None)
        for job in jobs:
            _remove_id_field(job)
        jobs = [ProtocaasJob(**job) for job in jobs] # validate jobs
        for job in jobs:
            job.jobPrivateKey = '' # hide the private key
        return GetProjectJobsResponse(jobs=jobs, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))