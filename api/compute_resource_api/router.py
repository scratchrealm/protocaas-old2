import os
import time
from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._crypto_keys import _verify_signature_str

router = APIRouter()

# get apps
@router.get("/api/compute_resource/compute_resources/{compute_resource_id}/apps")
async def compute_resource_get_apps(compute_resource_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        expected_payload = f'/api/compute_resource/compute_resources/{compute_resource_id}/apps'
        _authenticate_compute_resource_request(headers, compute_resource_id, expected_payload)

        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        apps = compute_resource['apps']
        return {'apps': apps, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get pubsub subscription
@router.get("/api/compute_resource/compute_resources/{compute_resource_id}/pubsub_subscription")
async def compute_resource_get_pubsub_subscription(compute_resource_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        expected_payload = f'/api/compute_resource/compute_resources/{compute_resource_id}/pubsub_subscription'
        _authenticate_compute_resource_request(headers, compute_resource_id, expected_payload)

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

# get unfinished jobs
@router.get("/api/compute_resource/compute_resources/{compute_resource_id}/unfinished_jobs")
async def compute_resource_get_unfinished_jobs(compute_resource_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        expected_payload = f'/api/compute_resource/compute_resources/{compute_resource_id}/unfinished_jobs'
        _authenticate_compute_resource_request(headers, compute_resource_id, expected_payload)

        compute_resource_node_id = headers['compute-resource-node-id']
        compute_resource_node_name = headers['compute-resource-node-name']

        client = _get_mongo_client()
        jobs_collection = client['protocaas']['jobs']
        jobs = await jobs_collection.find({
            'computeResourceId': compute_resource_id,
            'status': {'$in': ['pending', 'queued', 'starting', 'running']}
        }).to_list(length=None)

        compute_resource_nodes_collection = client['protocaas']['computeResourceNodes']
        await compute_resource_nodes_collection.update_one({
            'computeResourceId': compute_resource_id,
            'nodeId': compute_resource_node_id
        }, {
            '$set': {
                'timestampLastActive': time.time(),
                'computeResourceId': compute_resource_id,
                'nodeId': compute_resource_node_id,
                'nodeName': compute_resource_node_name
            }
        }, upsert=True)
        
        return {'jobs': jobs, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set spec
@router.put("/api/compute_resource/compute_resources/{compute_resource_id}/spec")
async def compute_resource_set_spec(compute_resource_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        expected_payload = f'/api/compute_resource/compute_resources/{compute_resource_id}/spec'
        _authenticate_compute_resource_request(headers, compute_resource_id, expected_payload)

        data = await request.json()
        spec = data['spec']

        client = _get_mongo_client()
        compute_resources_collection = client['protocaas']['computeResources']
        compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
        if compute_resource is None:
            raise Exception(f"No compute resource with ID {compute_resource_id}")
        await compute_resources_collection.update_one({'computeResourceId': compute_resource_id}, {
            '$set': {
                'spec': spec
            }
        })

        return {'success': True}
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