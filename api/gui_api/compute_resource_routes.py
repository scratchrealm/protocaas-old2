import os
import time
from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field
from ..common._crypto_keys import _verify_signature
from ._authenticate_gui_request import _authenticate_gui_request


router = APIRouter()

# get compute resource
@router.get("/api/gui/compute_resources/{compute_resource_id}")
async def get_compute_resource(compute_resource_id, request: Request):
    try:
        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        _remove_id_field(compute_resource)
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        return {'computeResource': compute_resource, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get compute resources
@router.get("/api/gui/compute_resources")
async def get_compute_resources(request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if not user_id:
            raise Exception('User is not authenticated')
        
        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resources = await compute_resources_collection.find({'ownerId': user_id}).to_list(length=None)
        for compute_resource in compute_resources:
            _remove_id_field(compute_resource)
        return {'computeResources': compute_resources, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set compute resource apps
@router.put("/api/gui/compute_resources/{compute_resource_id}/apps")
async def set_compute_resource_apps(compute_resource_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        body = await request.json()
        apps = body['apps']

        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        if compute_resource['ownerId'] != user_id:
            raise Exception('User does not have permission to admin this compute resource')
        
        compute_resources_collection.update_one({'computeResourceId': compute_resource_id}, {
            '$set': {
                'apps': apps,
                'timestampModified': time.time()
            }
        })

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete compute resource
@router.delete("/api/gui/compute_resources/{compute_resource_id}")
async def delete_compute_resource(compute_resource_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        if compute_resource['ownerId'] != user_id:
            raise Exception('User does not have permission to delete this compute resource')
        
        compute_resources_collection.delete_one({'computeResourceId': compute_resource_id})

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get pubsub subscription
@router.get("/api/gui/compute_resources/{compute_resource_id}/pubsub_subscription")
async def get_pubsub_subscription(compute_resource_id, request: Request):
    try:
        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        VITE_PUBNUB_SUBSCRIBE_KEY = os.environ.get('VITE_PUBNUB_SUBSCRIBE_KEY')
        if VITE_PUBNUB_SUBSCRIBE_KEY is None:
            raise Exception('Environment variable not set: VITE_PUBNUB_SUBSCRIBE_KEY')
        subscription = {
            'pubnubSubscribeKey': VITE_PUBNUB_SUBSCRIBE_KEY,
            'pubnubChannel': compute_resource_id,
            'pubnubUser': compute_resource_id
        }
        return {'subscription': subscription, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# register compute resource
@router.post("/api/gui/compute_resources/register")
async def register_compute_resource(request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if user_id is None:
            raise Exception('User is not authenticated')
        
        # parse the request
        body = await request.json()
        compute_resource_id = body['computeResourceId']
        resource_code = body['resourceCode']
        name = body['name']
        
        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']

        ok = await _verify_resource_code(compute_resource_id, resource_code)
        if not ok:
            raise Exception('Invalid resource code')
        
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        if compute_resource is not None:
            compute_resources_collection.update_one({'computeResourceId': compute_resource_id}, {
                '$set': {
                    'ownerId': user_id,
                    'name': name,
                    'timestampModified': time.time()
                }
            })
        else:
            compute_resources_collection.insert_one({
                'computeResourceId': compute_resource_id,
                'ownerId': user_id,
                'name': name,
                'timestampCreated': time.time(),
                'apps': []
            })
        
        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get jobs for compute resource
@router.get("/api/gui/compute_resources/{compute_resource_id}/jobs")
async def get_jobs_for_compute_resource(compute_resource_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        if compute_resource['ownerId'] != user_id:
            raise Exception('User does not have permission to view jobs for this compute resource')

        jobs_collection = client['protocaas']['jobs']
        jobs = await jobs_collection.find({
            'computeResourceId': compute_resource_id
        }).to_list(length=None)
        for job in jobs:
            _remove_id_field(job)
            job['jobPrivateKey'] = '' # hide the private key
        return {'jobs': jobs, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _verify_resource_code(compute_resource_id: str, resource_code: str) -> bool:
    # check that timestamp is within 5 minutes of current time
    timestamp = int(resource_code.split('-')[0])
    if abs(timestamp - time.time()) > 300:
        return False
    signature = resource_code.split('-')[1]
    if not _verify_signature({'timestamp': timestamp}, compute_resource_id, signature):
        return False
    return True