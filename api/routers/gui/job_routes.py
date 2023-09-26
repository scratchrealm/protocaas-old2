from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from ...services._remove_detached_files_and_jobs import _remove_detached_files_and_jobs
from ...core.protocaas_types import ProtocaasJob
from ._authenticate_gui_request import _authenticate_gui_request
from ...core._get_workspace_role import _get_workspace_role
from ...clients.db import fetch_job, fetch_workspace, delete_job as db_delete_job


router = APIRouter()

# get job
class GetJobResponse(BaseModel):
    job: ProtocaasJob
    success: bool

@router.get("/{job_id}")
async def get_job(job_id, request: Request) -> GetJobResponse:
    try:
        job = await fetch_job(job_id)
        if job is None:
            raise Exception(f"No job with ID {job_id}")
        return GetJobResponse(job=job, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete job
class DeleteJobResponse(BaseModel):
    success: bool

@router.delete("/{job_id}")
async def delete_job(job_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if not user_id:
            raise Exception('User is not authenticated')

        job = await fetch_job(job_id)
        if job is None:
            raise Exception(f"No job with ID {job_id}")
        
        workspace_id = job.workspaceId
        workspace = await fetch_workspace(workspace_id)
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to delete jobs in this project')
        
        await db_delete_job(job_id)

        # remove detached files and jobs
        await _remove_detached_files_and_jobs(job.projectId)

        return DeleteJobResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))