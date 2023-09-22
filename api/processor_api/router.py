import os
import time
from fastapi import APIRouter, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
from ..common._get_mongo_client import _get_mongo_client
from ..common._pubsub import _publish_pubsub_message
from ..common._create_output_file import _create_output_file
from ..common._get_signed_upload_url import _get_signed_upload_url
from ..common._remove_id_field import _remove_id_field

router = APIRouter()

# get job
@router.get("/api/processor/jobs/{job_id}")
async def processor_get_job(job_id: str, request: Request):
    try:
        headers = request.headers
        job_private_key = headers['job-private-key']

        client = _get_mongo_client()

        client: AsyncIOMotorClient = _get_mongo_client()
        jobs_collection = client['protocaas']['jobs']
        job = await jobs_collection.find_one({'jobId': job_id})
        _remove_id_field(job)
        if job is None:
            raise Exception(f"No job with ID {job_id}")
        if job['jobPrivateKey'] != job_private_key:
            raise Exception(f"Invalid job private key for job {job_id}")
        print(job['status'])
        return {'job': job, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# update job status
@router.put("/api/processor/jobs/{job_id}/status")
async def processor_update_job_status(job_id: str, request: Request):
    try:
        # make sure we can get the job - proves that the job exists and that the job private key is valid
        resp = await processor_get_job(job_id, request)
        job = resp['job']

        old_status = job['status']

        # get the status from the request body
        data = await request.json()
        new_status = data['status']

        client = _get_mongo_client()
        jobs_collection = client['protocaas']['jobs']

        if new_status == 'starting':
            if old_status != 'pending':
                raise Exception(f"Cannot set job status to starting when status is {old_status}")
        elif new_status == 'running':
            if old_status != 'starting':
                raise Exception(f"Cannot set job status to running when status is {old_status}")
        elif new_status == 'completed':
            if old_status != 'running':
                raise Exception(f"Cannot set job status to completed when status is {old_status}")
        elif new_status == 'failed':
            if (old_status != 'running') and (old_status != 'starting') and (old_status != 'pending'):
                raise Exception(f"Cannot set job status to failed when status is {old_status}")
        
        if 'error' in data:
            if new_status != 'failed':
                raise Exception(f"Cannot set job error when status is {new_status}")
        if new_status == 'completed':
            # we need to create the output files before marking the job as completed
            output_bucket_base_url = os.environ.get('OUTPUT_BUCKET_BASE_URL')
            if output_bucket_base_url is None:
                raise Exception('Environment variable not set: OUTPUT_BUCKET_BASE_URL')
            output_file_ids = []
            for output_file in job['outputFiles']:
                output_file_url = f"{output_bucket_base_url}/protocaas-outputs/{job_id}/{output_file['name']}"
                output_file_id = await _create_output_file(
                    file_name=output_file['fileName'],
                    url=output_file_url,
                    workspace_id=job['workspaceId'],
                    project_id=job['projectId'],
                    user_id=job['userId'],
                    job_id=job['jobId']
                )
                output_file_ids.append(output_file_id)
                output_file['fileId'] = output_file_id
            await jobs_collection.update_one({
                'jobId': job_id
            }, {
                '$set': {
                    'outputFiles': job['outputFiles'],
                    'outputFileIds': output_file_ids
                }
            })
        update = {}
        update['status'] = new_status
        if 'error' in data:
            update['error'] = data['error']
        if new_status == 'queued':
            update['timestampQueued'] = time.time()
        elif new_status == 'starting':
            update['timestampStarting'] = time.time()
        elif new_status == 'running':
            update['timestampStarted'] = time.time()
        elif new_status == 'completed':
            update['timestampFinished'] = time.time()
        elif new_status == 'failed':
            update['timestampFinished'] = time.time()
        await jobs_collection.update_one({
            'jobId': job_id
        }, {
            '$set': update
        })

        await _publish_pubsub_message(
            channel=job['computeResourceId'],
            message={
                'type': 'jobStatusChanged',
                'workspaceId': job['workspaceId'],
                'projectId': job['projectId'],
                'computeResourceId': job['computeResourceId'],
                'jobId': job['jobId'],
                'status': new_status
            }
        )

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set job console output
@router.put("/api/processor/jobs/{job_id}/console_output")
async def processor_set_job_console_output(job_id: str, request: Request):
    try:
        # make sure we can get the job - proves that the job exists and that the job private key is valid
        resp = await processor_get_job(job_id, request)
        job = resp['job']

        # get the console output from the request body
        data = await request.json()
        console_output = data['consoleOutput']

        client = _get_mongo_client()
        jobs_collection = client['protocaas']['jobs']

        await jobs_collection.update_one({
            'jobId': job_id
        }, {
            '$set': {
                'consoleOutput': console_output
            }
        })

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get job output upload url
@router.get("/api/processor/jobs/{job_id}/outputs/{output_name}/upload_url")
async def processor_get_upload_url(job_id: str, output_name: str, request: Request):
    try:
        # getting the job proves that the job exists and that the job private key is valid
        resp = await processor_get_job(job_id, request)
        job = resp['job']
        aa = [x for x in job['outputFiles'] if x['name'] == output_name]
        if len(aa) == 0:
            raise Exception(f"No output with name {output_name}")
        
        object_key = f"protocaas-outputs/{job_id}/{output_name}"

        OUTPUT_BUCKET_URI = os.environ.get('OUTPUT_BUCKET_URI')
        if OUTPUT_BUCKET_URI is None:
            raise Exception('Environment variable not set: OUTPUT_BUCKET_URI')
        OUTPUT_BUCKET_CREDENTIALS = os.environ.get('OUTPUT_BUCKET_CREDENTIALS')
        if OUTPUT_BUCKET_CREDENTIALS is None:
            raise Exception('Environment variable not set: OUTPUT_BUCKET_CREDENTIALS')
        
        signed_upload_url = await _get_signed_upload_url(
            bucket_uri=OUTPUT_BUCKET_URI,
            bucket_credentials=OUTPUT_BUCKET_CREDENTIALS,
            object_key=object_key
        )
        return {'uploadUrl': signed_upload_url, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))