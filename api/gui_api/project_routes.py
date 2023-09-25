import time
from fastapi import APIRouter, HTTPException, Request
from ..common._get_mongo_client import _get_mongo_client
from ..common._remove_id_field import _remove_id_field
from ..common._create_random_id import _create_random_id
from ._authenticate_gui_request import _authenticate_gui_request
from ._get_workspace_role import _get_workspace_role


router = APIRouter()

# get project
@router.get("/api/gui/projects/{project_id}")
async def get_project(project_id, request: Request):
    try:
        client = _get_mongo_client()
        projects_collection = client['protocaas']['projects']
        project = await projects_collection.find_one({'projectId': project_id})
        _remove_id_field(project)
        if project is None:
            raise Exception(f"No project with ID {project_id}")
        return {'project': project, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get projects
@router.get("/api/gui/projects")
async def get_projects(request: Request):
    try:
        # parse the request
        body = await request.json()
        workspace_id = body['workspaceId']

        client = _get_mongo_client()
        projects_collection = client['protocaas']['projects']
        projects = await projects_collection.find({'workspaceId': workspace_id}).to_list(length=None)
        for project in projects:
            _remove_id_field(project)
        return {'projects': projects, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# create project
@router.post("/api/gui/projects")
async def create_project(request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        body = await request.json()
        workspace_id = body['workspaceId']
        name = body['name']

        client = _get_mongo_client()
        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to create projects')
        
        project_id = _create_random_id(8)
        project = {
            'projectId': project_id,
            'workspaceId': workspace_id,
            'name': name,
            'description': '',
            'timestampCreated': time.time(),
            'timestampModified': time.time()
        }
        projects_collection = client['protocaas']['projects']
        await projects_collection.insert_one(project)

        await workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'timestampModified': time.time()
            }
        })

        return {'projectId': project_id, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# set project name
@router.put("/api/gui/projects/{project_id}/name")
async def set_project_name(project_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        # parse the request
        body = await request.json()
        name = body['name']

        client = _get_mongo_client()
        projects_collection = client['protocaas']['projects']
        project = await projects_collection.find_one({'projectId': project_id})
        if project is None:
            raise Exception(f"No project with ID {project_id}")
        workspace_id = project['workspaceId']

        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin' and workspace_role != 'editor':
            raise Exception('User does not have permission to edit projects')
        
        projects_collection.update_one({'projectId': project_id}, {
            '$set': {
                'name': name,
                'timestampModified': time.time()
            }
        })

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# delete project
@router.delete("/api/gui/projects/{project_id}")
async def delete_project(project_id, request: Request):
    try:
        # authenticate the request
        headers = request.headers
        user_id = await _authenticate_gui_request(headers)

        client = _get_mongo_client()
        projects_collection = client['protocaas']['projects']
        project = await projects_collection.find_one({'projectId': project_id})
        if project is None:
            raise Exception(f"No project with ID {project_id}")
        workspace_id = project['workspaceId']

        workspaces_collection = client['protocaas']['workspaces']
        workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
        if workspace is None:
            raise Exception(f"No workspace with ID {workspace_id}")
        workspace_role = _get_workspace_role(workspace, user_id)
        if workspace_role != 'admin':
            raise Exception('User does not have permission to delete projects')
        
        files_collection = client['protocaas']['files']
        await files_collection.delete_many({'projectId': project_id})

        jobs_collection = client['protocaas']['jobs']
        await jobs_collection.delete_many({'projectId': project_id})

        await projects_collection.delete_one({'projectId': project_id})

        workspaces_collection.update_one({'workspaceId': workspace_id}, {
            '$set': {
                'timestampModified': time.time()
            }
        })

        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# get jobs
@router.get("/api/gui/projects/{project_id}/jobs")
async def get_jobs(project_id, request: Request):
    try:
        client = _get_mongo_client()
        jobs_collection = client['protocaas']['jobs']
        jobs = await jobs_collection.find({
            'projectId': project_id
        }).to_list(length=None)
        for job in jobs:
            _remove_id_field(job)
            job['jobPrivateKey'] = '' # hide the private key
        return {'jobs': jobs, 'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))