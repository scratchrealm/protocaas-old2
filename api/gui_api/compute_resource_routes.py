from typing import Union, List, Any
import os
import time
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field
from ..common._crypto_keys import _verify_signature
from ..common.protocaas_types import ProtocaasComputeResource, ProtocaasComputeResourceApp, PubsubSubscription, ProtocaasJob
from ._authenticate_gui_request import _authenticate_gui_request


router = APIRouter()

# get compute resource
class GetComputeResourceResponse(BaseModel):
    computeResource: ProtocaasComputeResource
    success: bool

@router.get("/api/gui/compute_resources/{compute_resource_id}")
async def get_compute_resource(compute_resource_id, request: Request) -> GetComputeResourceResponse:
    try:
        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        _remove_id_field(compute_resource)
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        compute_resource = ProtocaasComputeResource(**compute_resource) # validate compute resource
        return GetComputeResourceResponse(computeResource=compute_resource, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get compute resources
class GetComputeResourcesResponse(BaseModel):
    computeResources: List[ProtocaasComputeResource]
    success: bool

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
        compute_resources = [ProtocaasComputeResource(**compute_resource) for compute_resource in compute_resources] # validate compute resources
        return GetComputeResourcesResponse(computeResources=compute_resources, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set compute resource apps
class SetComputeResourceAppsRequest(BaseModel):
    apps: List[ProtocaasComputeResourceApp]

class SetComputeResourceAppsResponse(BaseModel):
    success: bool

@router.put("/api/gui/compute_resources/{compute_resource_id}/apps")
async def set_compute_resource_apps(compute_resource_id, data: SetComputeResourceAppsRequest, request: Request) -> SetComputeResourceAppsResponse:
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        apps = data.apps

        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        compute_resource = ProtocaasComputeResource(**compute_resource) # validate compute resource
        if compute_resource.ownerId != user_id:
            raise Exception('User does not have permission to admin this compute resource')
        
        compute_resources_collection.update_one({'computeResourceId': compute_resource_id}, {
            '$set': {
                'apps': apps,
                'timestampModified': time.time()
            }
        })

        return SetComputeResourceAppsResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete compute resource
class DeleteComputeResourceResponse(BaseModel):
    success: bool

@router.delete("/api/gui/compute_resources/{compute_resource_id}")
async def delete_compute_resource(compute_resource_id, request: Request) -> DeleteComputeResourceResponse:
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        compute_resource = ProtocaasComputeResource(**compute_resource) # validate compute resource
        if compute_resource.ownerId != user_id:
            raise Exception('User does not have permission to delete this compute resource')
        
        compute_resources_collection.delete_one({'computeResourceId': compute_resource_id})

        return DeleteComputeResourceResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get pubsub subscription
class GetPubsubSubscriptionResponse(BaseModel):
    subscription: PubsubSubscription
    success: bool

@router.get("/api/gui/compute_resources/{compute_resource_id}/pubsub_subscription")
async def get_pubsub_subscription(compute_resource_id, request: Request):
    try:
        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        compute_resource = ProtocaasComputeResource(**compute_resource) # validate compute resource
        VITE_PUBNUB_SUBSCRIBE_KEY = os.environ.get('VITE_PUBNUB_SUBSCRIBE_KEY')
        if VITE_PUBNUB_SUBSCRIBE_KEY is None:
            raise Exception('Environment variable not set: VITE_PUBNUB_SUBSCRIBE_KEY')
        subscription = PubsubSubscription(
            pubnubSubscribeKey=VITE_PUBNUB_SUBSCRIBE_KEY,
            pubnubChannel=compute_resource_id,
            pubnubUser=compute_resource_id
        )
        return GetPubsubSubscriptionResponse(subscription=subscription, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# register compute resource
class RegisterComputeResourceRequest(BaseModel):
    computeResourceId: str
    resourceCode: str
    name: str

class RegisterComputeResourceResponse(BaseModel):
    success: bool

@router.post("/api/gui/compute_resources/register")
async def register_compute_resource(data: RegisterComputeResourceRequest, request: Request) -> RegisterComputeResourceResponse:
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if user_id is None:
            raise Exception('User is not authenticated')
        
        # parse the request
        compute_resource_id = data.computeResourceId
        resource_code = data.resourceCode
        name = data.name
        
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
            new_compute_resource = ProtocaasComputeResource(
                computeResourceId=compute_resource_id,
                ownerId=user_id,
                name=name,
                timestampCreated=time.time(),
                apps=[]
            )
            compute_resources_collection.insert_one(new_compute_resource)
        
        return RegisterComputeResourceResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get jobs for compute resource
class GetJobsForComputeResourceResponse(BaseModel):
    jobs: List[Any]
    success: bool

@router.get("/api/gui/compute_resources/{compute_resource_id}/jobs")
async def get_jobs_for_compute_resource(compute_resource_id, request: Request) -> GetJobsForComputeResourceResponse:
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        compute_resource = ProtocaasComputeResource(**compute_resource) # validate compute resource
        if compute_resource.ownerId != user_id:
            raise Exception('User does not have permission to view jobs for this compute resource')

        jobs_collection = client['protocaas']['jobs']
        jobs = await jobs_collection.find({
            'computeResourceId': compute_resource_id
        }).to_list(length=None)
        for job in jobs:
            _remove_id_field(job)
        jobs = [ProtocaasJob(**job) for job in jobs] # validate jobs
        for job in jobs:
            job.jobPrivateKey = '' # hide the private key
        return GetJobsForComputeResourceResponse(jobs=jobs, success=True)
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