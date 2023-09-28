from typing import Union, List, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request
from ._authenticate_gui_request import _authenticate_gui_request
from ...services.gui.create_job import create_job
from ...core.protocaas_types import ComputeResourceSpecProcessor


router = APIRouter()

# create job
class CreateJobRequestInputFile(BaseModel):
    name: str
    fileName: str

class CreateJobRequestOutputFile(BaseModel):
    name: str
    fileName: str

class CreateJobRequestInputParameter(BaseModel):
    name: str
    value: Union[Any, None]

class CreateJobRequest(BaseModel):
    workspaceId: str
    projectId: str
    processorName: str
    inputFiles: List[CreateJobRequestInputFile]
    outputFiles: List[CreateJobRequestOutputFile]
    inputParameters: List[CreateJobRequestInputParameter]
    processorSpec: ComputeResourceSpecProcessor
    batchId: Union[str, None] = None

class CreateJobResponse(BaseModel):
    jobId: str
    success: bool

@router.post("/jobs")
async def create_job_handler(data: CreateJobRequest, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if not user_id:
            raise Exception('User is not authenticated')

        # parse the request
        workspace_id = data.workspaceId
        project_id = data.projectId
        processor_name = data.processorName
        input_files_from_request = data.inputFiles
        output_files_from_request = data.outputFiles
        input_parameters = data.inputParameters
        processor_spec = data.processorSpec
        batch_id = data.batchId

        job_id = await create_job(
            workspace_id=workspace_id,
            project_id=project_id,
            processor_name=processor_name,
            input_files_from_request=input_files_from_request,
            output_files_from_request=output_files_from_request,
            input_parameters=input_parameters,
            processor_spec=processor_spec,
            batch_id=batch_id,
            user_id=user_id
        )

        return CreateJobResponse(
            jobId=job_id,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))