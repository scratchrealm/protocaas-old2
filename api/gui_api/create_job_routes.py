import os
import time
from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_detached_files_and_jobs import _remove_detached_files_and_jobs
from ..common._pubsub import _publish_pubsub_message
from ..common._create_random_id import _create_random_id
from ._authenticate_gui_request import _authenticate_gui_request
from ._get_workspace_role import _get_workspace_role


router = APIRouter()

# create job
@router.post("/api/gui/jobs")
async def create_job_handler(request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        body = await request.json()
        workspace_id = body['workspaceId']
        project_id = body['projectId']
        processor_name = body['processorName']
        input_files_from_request = body['inputFiles']
        output_files_from_request = body['outputFiles']
        input_parameters = body['inputParameters']
        processor_spec = body['processorSpec']
        batch_id = body.get('batchId', None)

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to create jobs')
        
        compute_resource_id = workspace.get('computeResourceId', None)
        if compute_resource_id is None:
            compute_resource_id = os.environ.get('VITE_DEFAULT_COMPUTE_RESOURCE_ID')
            if compute_resource_id is None:
                raise Exception('Workspace does not have a compute resource ID, and no default VITE_DEFAULT_COMPUTE_RESOURCE_ID is set in the environment.')
        
        projects_collection = client['protocaas']['projects']
        project = await projects_collection.find_one({'projectId': body['projectId']})
        # important to check this
        if project['workspaceId'] != workspace_id:
            raise Exception('Incorrect workspace ID for project')
        
        files_collection = client['protocaas']['files']
        input_files = [] # {name, fileId, fileName}
        for input_file in input_files_from_request:
            file = await files_collection.find_one({
                'projectId': body['projectId'],
                'fileName': input_file['fileName']
            })
            if file is None:
                raise Exception(f"Project input file does not exist: {input_file['fileName']}")
            input_files.append({
                'name': input_file['name'],
                'fileId': file['fileId'],
                'fileName': file['fileName']
            })
        
        job_id = _create_random_id(8)
        job_private_key = _create_random_id(32)

        def filter_output_file_name(file_name):
            # replace ${job-id} with the actual job ID
            return file_name.replace('${job-id}', job_id)
        
        output_files = []
        for output_file in output_files_from_request:
            output_files.append({
                **output_file,
                'fileName': filter_output_file_name(output_file['fileName'])
            })
        
        something_was_deleted = False
        
        # delete any existing output files
        for output_file in output_files:
            existing_file = await files_collection.find_one({
                'projectId': body['projectId'],
                'fileName': output_file['fileName']
            })
            if existing_file is not None:
                await files_collection.delete_one({
                    'projectId': body['projectId'],
                    'fileName': output_file['fileName']
                })
                something_was_deleted = True
        
        # delete any jobs that are expected to produce the output files
        # because maybe the output files haven't been created yet, but we still want to delete/cancel them
        jobs_collection = client['protocaas']['jobs']
        all_jobs = await jobs_collection.find({
            'projectId': body['projectId']
        }).to_list(length=None)
        output_file_names = [x['fileName'] for x in output_files]
        for job in all_jobs:
            should_delete = False
            for output_file in job.get('outputFiles', []):
                if output_file['fileName'] in output_file_names:
                    should_delete = True
            if should_delete:
                await jobs_collection.delete_one({
                    'projectId': body['projectId'],
                    'jobId': job['jobId']
                })
                something_was_deleted = True
        
        if something_was_deleted:
            await _remove_detached_files_and_jobs(body['projectId'])
        
        job = {
            'jobId': job_id,
            'jobPrivateKey': job_private_key,
            'workspaceId': workspace_id,
            'projectId': project_id,
            'userId': user_id,
            'processorName': processor_name,
            'inputFiles': input_files,
            'inputFileIds': [x['fileId'] for x in input_files],
            'inputParameters': input_parameters,
            'outputFiles': output_files,
            'timestampCreated': time.time(),
            'computeResourceId': compute_resource_id,
            'status': 'pending',
            'processorSpec': processor_spec
        }
        if batch_id is not None:
            job['batchId'] = batch_id
        
        await jobs_collection.insert_one(job)

        await _publish_pubsub_message(
            channel=job['computeResourceId'],
            message={
                'type': 'newPendingJob',
                'workspaceId': workspace_id,
                'projectId': project_id,
                'computeResourceId': compute_resource_id,
                'jobId': job_id
            }
        )

        return {'jobId': job_id, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))