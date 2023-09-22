import time
from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field


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