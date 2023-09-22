from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field

router = APIRouter()

# get project
@router.get("/api/client/projects/{project_id}")
async def get_project(project_id, request: Request):
    try:
        client = _get_mongo_client()
        projects_collection = client['protocaas']['projects']
        project = await projects_collection.find_one({'projectId': project_id})
        _remove_id_field(project)
        if project is None:
            raise Exception(f"No project with ID {project_id}")
        return {'project': project, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get project files
@router.get("/api/client/projects/{project_id}/files")
async def get_project_files(project_id, request: Request):
    try:
        client = _get_mongo_client()
        files_collection = client['protocaas']['files']
        files = await files_collection.find({'projectId': project_id}).to_list(length=None)
        for file in files:
            _remove_id_field(file)
        return {'files': files, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get project jobs
@router.get("/api/client/projects/{project_id}/jobs")
async def get_project_jobs(project_id, request: Request):
    try:
        client = _get_mongo_client()
        jobs_collection = client['protocaas']['jobs']
        jobs = await jobs_collection.find({'projectId': project_id}).to_list(length=None)
        for job in jobs:
            _remove_id_field(job)
        job['jobPrivateKey'] = '' # hide the private key
        return {'jobs': jobs, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))