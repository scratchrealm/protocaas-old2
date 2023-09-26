from typing import Union, List, Any
import os
import time
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_detached_files_and_jobs import _remove_detached_files_and_jobs
from ..common._pubsub import _publish_pubsub_message
from ..common._create_random_id import _create_random_id
from ..common._remove_id_field import _remove_id_field
from ..common.protocaas_types import ProtocaasWorkspace, ProtocaasProject, ProtocaasJob, ProtocaasFile, ProtocaasJobInputFile, ProtocaasJobOutputFile, ProtocaasJobInputParameter, ComputeResourceSpecProcessor
from ._authenticate_gui_request import _authenticate_gui_request
from ._get_workspace_role import _get_workspace_role


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

@router.post("/api/gui/jobs")
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

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        _remove_id_field(workspace)
        workspace = ProtocaasWorkspace(**workspace) # validate workspace
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to create jobs')
        
        compute_resource_id = workspace.computeResourceId
        if compute_resource_id is None:
            compute_resource_id = os.environ.get('VITE_DEFAULT_COMPUTE_RESOURCE_ID')
            if compute_resource_id is None:
                raise Exception('Workspace does not have a compute resource ID, and no default VITE_DEFAULT_COMPUTE_RESOURCE_ID is set in the environment.')
        
        projects_collection = client['protocaas']['projects']
        project = await projects_collection.find_one({'projectId': project_id})
        if project is None:
            raise Exception(f"No project with ID {project_id}")
        _remove_id_field(project)
        project = ProtocaasProject(**project) # validate project
        # important to check this
        if project.workspaceId != workspace_id:
            raise Exception('Incorrect workspace ID for project')
        
        files_collection = client['protocaas']['files']
        input_files: List[ProtocaasJobInputFile] = [] # {name, fileId, fileName}
        for input_file in input_files_from_request:
            file = await files_collection.find_one({
                'projectId': project_id,
                'fileName': input_file.fileName
            })
            if file is None:
                raise Exception(f"Project input file does not exist: {input_file.fileName}")
            _remove_id_field(file)
            file = ProtocaasFile(**file)
            input_files.append(
                ProtocaasJobInputFile(
                    name=input_file.name,
                    fileId=file.fileId,
                    fileName=file.fileName
                )
            )
        
        job_id = _create_random_id(8)
        job_private_key = _create_random_id(32)

        def filter_output_file_name(file_name):
            # replace ${job-id} with the actual job ID
            return file_name.replace('${job-id}', job_id)
        
        output_files: List[ProtocaasJobOutputFile] = []
        for output_file in output_files_from_request:
            output_files.append(
                ProtocaasJobOutputFile(
                    name=output_file.name,
                    fileName=filter_output_file_name(output_file.fileName)
                )
            )
        
        something_was_deleted = False
        
        # delete any existing output files
        for output_file in output_files:
            existing_file = await files_collection.find_one({
                'projectId': project_id,
                'fileName': output_file.fileName
            })
            if existing_file is not None:
                await files_collection.delete_one({
                    'projectId': project_id,
                    'fileName': output_file.fileName
                })
                something_was_deleted = True
        
        # delete any jobs that are expected to produce the output files
        # because maybe the output files haven't been created yet, but we still want to delete/cancel them
        jobs_collection = client['protocaas']['jobs']
        all_jobs = await jobs_collection.find({
            'projectId': project_id
        }).to_list(length=None)
        for job in all_jobs:
            _remove_id_field(job)
        all_jobs = [ProtocaasJob(**x) for x in all_jobs]
        output_file_names = [x.fileName for x in output_files]
        for job in all_jobs:
            should_delete = False
            for output_file in job.outputFiles:
                if output_file.fileName in output_file_names:
                    should_delete = True
            if should_delete:
                await jobs_collection.delete_one({
                    'projectId': project_id,
                    'jobId': job.jobId
                })
                something_was_deleted = True
        
        if something_was_deleted:
            await _remove_detached_files_and_jobs(project_id)
        
        job = ProtocaasJob(
            jobId=job_id,
            jobPrivateKey=job_private_key,
            workspaceId=workspace_id,
            projectId=project_id,
            userId=user_id,
            processorName=processor_name,
            inputFiles=input_files,
            inputFileIds=[x.fileId for x in input_files],
            inputParameters=input_parameters,
            outputFiles=output_files,
            timestampCreated=time.time(),
            computeResourceId=compute_resource_id,
            status='pending',
            processorSpec=processor_spec,
            batchId=batch_id
        )
        
        await jobs_collection.insert_one(job.dict(exclude_none=True))

        await _publish_pubsub_message(
            channel=job.computeResourceId,
            message={
                'type': 'newPendingJob',
                'workspaceId': workspace_id,
                'projectId': project_id,
                'computeResourceId': compute_resource_id,
                'jobId': job_id
            }
        )

        return CreateJobResponse(
            jobId=job_id,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))