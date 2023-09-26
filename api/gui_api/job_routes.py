from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field
from ..common._remove_detached_files_and_jobs import _remove_detached_files_and_jobs
from ..common.protocaas_types import ProtocaasJob, ProtocaasWorkspace
from ._authenticate_gui_request import _authenticate_gui_request
from ._get_workspace_role import _get_workspace_role


router = APIRouter()

# get job
class GetJobResponse(BaseModel):
    job: ProtocaasJob
    success: bool

@router.get("/api/gui/jobs/{job_id}")
async def get_job(job_id, request: Request) -> GetJobResponse:
    try:
        client = _get_mongo_client()
        jobs_collection = client['protocaas']['jobs']
        job = await jobs_collection.find_one({
            'jobId': job_id
        })
        if job is None:
            raise Exception(f"No job with ID {job_id}")
        _remove_id_field(job)
        job = ProtocaasJob(**job) # validate job
        job.jobPrivateKey = '' # hide the private key
        return GetJobResponse(job=job, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete job
class DeleteJobResponse(BaseModel):
    success: bool

@router.delete("/api/gui/jobs/{job_id}")
async def delete_job(job_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        jobs_collection = client['protocaas']['jobs']
        job = await jobs_collection.find_one({
            'jobId': job_id
        })
        if job is None:
            raise Exception(f"No job with ID {job_id}")
        workspace_id = job['workspaceId']
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        _remove_id_field(workspace)
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to delete jobs in this project')

        jobs_collection.delete_one({
            'jobId': job_id
        })

        # remove detached files and jobs
        await _remove_detached_files_and_jobs(job['projectId'])

        return DeleteJobResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))