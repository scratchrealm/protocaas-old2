from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field
from ..common._remove_detached_files_and_jobs import _remove_detached_files_and_jobs
from ._authenticate_gui_request import _authenticate_gui_request
from ._get_workspace_role import _get_workspace_role


router = APIRouter()

# get job
@router.get("/api/gui/projects/{project_id}/jobs/{job_id}")
async def get_job(project_id, job_id, request: Request):
    try:
        client = _get_mongo_client()
        jobs_collection = client['protocaas']['jobs']
        job = await jobs_collection.find_one({
            'projectId': project_id,
            'jobId': job_id
        })
        _remove_id_field(job)
        if job is None:
            raise Exception(f"No job with ID {job_id} in project with ID {project_id}")
        job['jobPrivateKey'] = '' # hide the private key
        return {'job': job, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get jobs
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
            job['jobPrivateKey'] = '' # hide the private key
        return {'jobs': jobs, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete job
@router.delete("/api/gui/projects/{project_id}/jobs/{job_id}")
async def delete_job(project_id, job_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        jobs_collection = client['protocaas']['jobs']
        job = await jobs_collection.find_one({
            'projectId': project_id,
            'jobId': job_id
        })
        if job is None:
            raise Exception(f"No job with ID {job_id} in project with ID {project_id}")
        workspace_id = job['workspaceId']
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to delete jobs in this project')

        jobs_collection.delete_one({
            'projectId': project_id,
            'jobId': job_id
        })

        # remove detached files and jobs
        await _remove_detached_files_and_jobs(project_id)

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))