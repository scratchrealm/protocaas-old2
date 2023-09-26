from typing import Union
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from ...services.processor.update_job_status import update_job_status
from ...services.processor.get_upload_url import get_upload_url
from ...core.protocaas_types import ProtocaasJob
from ...clients.db import fetch_job, update_job

router = APIRouter()

# get job
class ProcessorGetJobResponse(BaseModel):
    job: ProtocaasJob
    success: bool

@router.get("/jobs/{job_id}")
async def processor_get_job(job_id: str, request: Request) -> ProcessorGetJobResponse:
    try:
        headers = request.headers
        job_private_key = headers['job-private-key']

        job = await fetch_job(job_id)
        if job is None:
            raise Exception(f"No job with ID {job_id}")
        
        if job.jobPrivateKey != job_private_key:
            raise Exception(f"Invalid job private key for job {job_id}")

        return ProcessorGetJobResponse(job=job, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# update job status
class ProcessorUpdateJobStatusRequest(BaseModel):
    status: str
    error: Union[str, None] = None

class ProcessorUpdateJobStatusResponse(BaseModel):
    success: bool

@router.put("/jobs/{job_id}/status")
async def processor_update_job_status(job_id: str, data: ProcessorUpdateJobStatusRequest, request: Request) -> ProcessorUpdateJobStatusResponse:
    try:
        job = await fetch_job(job_id)
        if job is None:
            raise Exception(f"No job with ID {job_id}")
        if job.jobPrivateKey != request.headers['job-private-key']:
            raise Exception(f"Invalid job private key for job {job_id}")
        
        await update_job_status(job=job, status=request.status, error=request.error)

        return ProcessorUpdateJobStatusResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set job console output
class ProcessorSetJobConsoleOutputRequest(BaseModel):
    consoleOutput: str

class ProcessorSetJobConsoleOutputResponse(BaseModel):
    success: bool

@router.put("/jobs/{job_id}/console_output")
async def processor_set_job_console_output(job_id: str, data: ProcessorSetJobConsoleOutputRequest, request: Request) -> ProcessorSetJobConsoleOutputResponse:
    try:
        job = await fetch_job(job_id)
        if job is None:
            raise Exception(f"No job with ID {job_id}")
        if job.jobPrivateKey != request.headers['job-private-key']:
            raise Exception(f"Invalid job private key for job {job_id}")

        # get the console output from the request body
        console_output = data.consoleOutput

        await update_job(
            job_id=job_id,
            update={
                'consoleOutput': console_output
            }
        )

        return ProcessorSetJobConsoleOutputResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get job output upload url
class ProcessorGetJobOutputUploadUrlResponse(BaseModel):
    uploadUrl: str
    success: bool

@router.get("/jobs/{job_id}/outputs/{output_name}/upload_url")
async def processor_get_upload_url(job_id: str, output_name: str, request: Request) -> ProcessorGetJobOutputUploadUrlResponse:
    try:
        job = await fetch_job(job_id)
        if job.jobPrivateKey != request.headers['job-private-key']:
            raise Exception(f"Invalid job private key for job {job_id}")
        
        signed_upload_url = await get_upload_url(job=job, output_name=output_name)
        return ProcessorGetJobOutputUploadUrlResponse(uploadUrl=signed_upload_url, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))