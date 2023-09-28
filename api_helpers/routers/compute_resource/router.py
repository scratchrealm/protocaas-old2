import os
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request
from ...services._crypto_keys import _verify_signature_str
from ...core.protocaas_types import ProtocaasComputeResourceApp, ProtocaasJob, ComputeResourceSpec, PubsubSubscription
from ...clients.db import fetch_compute_resource, fetch_compute_resource_jobs, update_compute_resource_node, set_compute_resource_spec

router = APIRouter()

# get apps
class GetAppsResponse(BaseModel):
    apps: List[ProtocaasComputeResourceApp]
    success: bool

@router.get("/compute_resources/{compute_resource_id}/apps")
async def compute_resource_get_apps(compute_resource_id, request: Request) -> GetAppsResponse:
    try:
        # authenticate the request
        headers = request.headers
        expected_payload = f'/api/compute_resource/compute_resources/{compute_resource_id}/apps'
        _authenticate_compute_resource_request(headers, compute_resource_id, expected_payload)

        compute_resource = await fetch_compute_resource(compute_resource_id)
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        apps = compute_resource.apps
        return GetAppsResponse(apps=apps, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get pubsub subscription
class GetPubsubSubscriptionResponse(BaseModel):
    subscription: PubsubSubscription
    success: bool

@router.get("/compute_resources/{compute_resource_id}/pubsub_subscription")
async def compute_resource_get_pubsub_subscription(compute_resource_id, request: Request) -> GetPubsubSubscriptionResponse:
    try:
        # authenticate the request
        headers = request.headers
        expected_payload = f'/api/compute_resource/compute_resources/{compute_resource_id}/pubsub_subscription'
        _authenticate_compute_resource_request(headers, compute_resource_id, expected_payload)

        compute_resource = await fetch_compute_resource(compute_resource_id)
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
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

# get unfinished jobs
class GetUnfinishedJobsResponse(BaseModel):
    jobs: List[ProtocaasJob]
    success: bool

@router.get("/compute_resources/{compute_resource_id}/unfinished_jobs")
async def compute_resource_get_unfinished_jobs(compute_resource_id, request: Request) -> GetUnfinishedJobsResponse:
    try:
        # authenticate the request
        headers = request.headers
        expected_payload = f'/api/compute_resource/compute_resources/{compute_resource_id}/unfinished_jobs'
        _authenticate_compute_resource_request(headers, compute_resource_id, expected_payload)

        compute_resource_node_id = headers['compute-resource-node-id']
        compute_resource_node_name = headers['compute-resource-node-name']

        jobs = await fetch_compute_resource_jobs(compute_resource_id, statuses=['pending', 'queued', 'starting', 'running'], include_private_keys=True)

        await update_compute_resource_node(
            compute_resource_id=compute_resource_id,
            compute_resource_node_id=compute_resource_node_id,
            compute_resource_node_name=compute_resource_node_name
        )
        
        return GetUnfinishedJobsResponse(jobs=jobs, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set spec
class SetSpecRequest(BaseModel):
    spec: ComputeResourceSpec

class SetSpecResponse(BaseModel):
    success: bool

@router.put("/compute_resources/{compute_resource_id}/spec")
async def compute_resource_set_spec(compute_resource_id, data: SetSpecRequest, request: Request) -> SetSpecResponse:
    try:
        # authenticate the request
        headers = request.headers
        expected_payload = f'/api/compute_resource/compute_resources/{compute_resource_id}/spec'
        _authenticate_compute_resource_request(headers, compute_resource_id, expected_payload)

        spec = data.spec

        await set_compute_resource_spec(compute_resource_id, spec)

        return SetSpecResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _authenticate_compute_resource_request(headers: dict, expected_compute_resource_id: str, expected_payload: str):
    compute_resource_id = headers['compute-resource-id']
    compute_resource_payload = headers['compute-resource-payload']
    compute_resource_signature = headers['compute-resource-signature']
    if compute_resource_id != expected_compute_resource_id:
        raise Exception('Unexpected compute resource ID')
    if compute_resource_payload != expected_payload:
        raise Exception('Unexpected payload')
    if not _verify_signature_str(compute_resource_payload, compute_resource_id, compute_resource_signature):
        raise Exception('Invalid signature')