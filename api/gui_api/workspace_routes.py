import time
from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field
from ..common._create_random_id import _create_random_id
from ._authenticate_gui_request import _authenticate_gui_request
from ._get_workspace_role import _get_workspace_role


router = APIRouter()

# create workspace
@router.post("/api/gui/workspaces")
async def create_workspace(request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)
        if not user_id:
            raise Exception('Unexpected: no user ID')

        # parse the request
        body = await request.json()
        name = body['name']

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace_id = _create_random_id(8)
        workspace = {
            'workspaceId': workspace_id,
            'ownerId': user_id,
            'name': name,
            'description': '',
            'users': [],
            'publiclyReadable': True,
            'listed': False,
            'timestampCreated': time.time(),
            'timestampModified': time.time()
        }
        await workspaces_collection.insert_one(workspace)

        return {'workspaceId': workspace_id, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get workspace
@router.get("/api/gui/workspaces/{workspace_id}")
async def get_workspace(workspace_id, request: Request):
    try:
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        _remove_id_field(workspace)
        role = _get_workspace_role(workspace, user_id)
        if role == 'none':
            raise Exception('User does not have permission to read this workspace')
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        return {'workspace': workspace, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get workspaces
@router.get("/api/gui/workspaces")
async def get_workspaces(request: Request):
    try:
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspaces = await workspaces_collection.find({}).to_list(length=None)
        for workspace in workspaces:
            _remove_id_field(workspace)
        workspaces2 = []
        for workspace in workspaces:
            role = _get_workspace_role(workspace, user_id)
            if role != 'none':
                workspaces2.append(workspace)
        return {'workspaces': workspaces2, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set workspace name
@router.put("/api/gui/workspaces/{workspace_id}/name")
async def set_workspace_name(workspace_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        body = await request.json()
        name = body['name']

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        role = _get_workspace_role(workspace, user_id)
        if role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'name': name,
                'timestampModified': time.time()
            }
        })

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set workspace publicly readable
@router.put("/api/gui/workspaces/{workspace_id}/publicly_readable")
async def set_workspace_public(workspace_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        body = await request.json()
        publicly_readable = body['publiclyReadable']

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        role = _get_workspace_role(workspace, user_id)
        if role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'publiclyReadable': publicly_readable,
                'timestampModified': time.time()
            }
        })

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# set workspace listed
@router.put("/api/gui/workspaces/{workspace_id}/listed")
async def set_workspace_listed(workspace_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        body = await request.json()
        listed = body['listed']

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        role = _get_workspace_role(workspace, user_id)
        if role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'listed': listed,
                'timestampModified': time.time()
            }
        })

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set workspace compute resource id
@router.put("/api/gui/workspaces/{workspace_id}/compute_resource_id")
async def set_workspace_compute_resource_id(workspace_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        body = await request.json()
        compute_resource_id = body['computeResourceId']

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        role = _get_workspace_role(workspace, user_id)
        if role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'computeResourceId': compute_resource_id,
                'timestampModified': time.time()
            }
        })

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set workspace users
@router.put("/api/gui/workspaces/{workspace_id}/users")
async def set_workspace_users(workspace_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        body = await request.json()
        users = body['users']

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        role = _get_workspace_role(workspace, user_id)
        if role != 'admin':
            raise Exception('User does not have permission to admin this workspace')
        
        workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'users': users,
                'timestampModified': time.time()
            }
        })

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete workspace
@router.delete("/api/gui/workspaces/{workspace_id}")
async def delete_workspace(workspace_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()

        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin':
            raise Exception('User does not have permission to delete this workspace')
        
        files_collection = client['protocaas']['files']
        await files_collection.delete_many({'workspaceId': workspace_id})

        jobs_collection = client['protocaas']['jobs']
        await jobs_collection.delete_many({'workspaceId': workspace_id})

        projects_collection = client['protocaas']['projects']
        await projects_collection.delete_many({'workspaceId': workspace_id})

        await workspaces_collection.delete_one({'workspaceId': workspace_id})

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get projects
@router.get("/api/gui/workspaces/{workspace_id}/projects")
async def get_workspace_projects(workspace_id, request: Request):
    try:
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        role = _get_workspace_role(workspace, user_id)
        if role == 'none':
            raise Exception('User does not have permission to read this workspace')

        projects_collection = client['protocaas']['projects']
        projects = await projects_collection.find({'workspaceId': workspace_id}).to_list(length=None)
        for project in projects:
            _remove_id_field(project)
        return {'projects': projects, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))