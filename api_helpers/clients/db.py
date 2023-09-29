import time
from typing import List, Union
from ._get_mongo_client import _get_mongo_client
from ._remove_id_field import _remove_id_field
from ..core.protocaas_types import ProtocaasProject, ProtocaasWorkspace, ProtocaasFile, ProtocaasJob, ProtocaasComputeResource, ComputeResourceSpec
from ..core._get_workspace_role import _get_workspace_role


async def fetch_workspace(workspace_id: str) -> ProtocaasWorkspace:
    client = _get_mongo_client()
    workspaces_collection = client['protocaas']['workspaces']
    workspace = await workspaces_collection.find_one({'workspaceId': workspace_id})
    _remove_id_field(workspace)
    if workspace is None:
        return None
    workspace = ProtocaasWorkspace(**workspace) # validate workspace
    return workspace

async def fetch_workspaces_for_user(user_id: Union[str, None]) -> List[ProtocaasWorkspace]:
    client = _get_mongo_client()
    workspaces_collection = client['protocaas']['workspaces']
    workspaces = await workspaces_collection.find({}).to_list(length=None)
    for workspace in workspaces:
        _remove_id_field(workspace)
    workspaces = [ProtocaasWorkspace(**workspace) for workspace in workspaces] # validate workspaces
    workspaces2: List[ProtocaasWorkspace] = []
    for workspace in workspaces:
        role = _get_workspace_role(workspace, user_id)
        if role != 'none':
            workspaces2.append(workspace)
    return workspaces2

async def update_workspace(workspace_id: str, update: dict):
    client = _get_mongo_client()
    workspaces_collection = client['protocaas']['workspaces']
    await workspaces_collection.update_one({
        'workspaceId': workspace_id
    }, {
        '$set': update
    })

async def insert_workspace(workspace: ProtocaasWorkspace):
    client = _get_mongo_client()
    workspaces_collection = client['protocaas']['workspaces']
    await workspaces_collection.insert_one(workspace.dict(exclude_none=True))

async def delete_all_files_in_workspace(workspace_id: str):
    client = _get_mongo_client()
    files_collection = client['protocaas']['files']
    await files_collection.delete_many({
        'workspaceId': workspace_id
    })

async def delete_all_jobs_in_workspace(workspace_id: str):
    client = _get_mongo_client()
    jobs_collection = client['protocaas']['jobs']
    await jobs_collection.delete_many({
        'workspaceId': workspace_id
    })

async def delete_all_projects_in_workspace(workspace_id: str):
    client = _get_mongo_client()
    projects_collection = client['protocaas']['projects']
    await projects_collection.delete_many({
        'workspaceId': workspace_id
    })

async def delete_workspace(workspace_id: str):
    client = _get_mongo_client()
    workspaces_collection = client['protocaas']['workspaces']
    await workspaces_collection.delete_one({
        'workspaceId': workspace_id
    })

async def fetch_projects_in_workspace(workspace_id: str) -> List[ProtocaasProject]:
    client = _get_mongo_client()
    projects_collection = client['protocaas']['projects']
    projects = await projects_collection.find({'workspaceId': workspace_id}).to_list(length=None)
    for project in projects:
        _remove_id_field(project)
    projects = [ProtocaasProject(**project) for project in projects] # validate projects
    return projects

async def fetch_project(project_id: str) -> ProtocaasProject:
    client = _get_mongo_client()
    projects_collection = client['protocaas']['projects']
    project = await projects_collection.find_one({'projectId': project_id})
    # here I'd like to validate project
    _remove_id_field(project)
    if project is None:
        return None
    return ProtocaasProject(**project) # validate project

async def fetch_project_files(project_id: str) -> List[ProtocaasFile]:
    client = _get_mongo_client()
    files_collection = client['protocaas']['files']
    files = await files_collection.find({'projectId': project_id}).to_list(length=None)
    for file in files:
        _remove_id_field(file)
    files = [ProtocaasFile(**file) for file in files] # validate files
    return files

async def fetch_project_jobs(project_id: str, include_private_keys=False) -> List[ProtocaasJob]:
    client = _get_mongo_client()
    jobs_collection = client['protocaas']['jobs']
    jobs = await jobs_collection.find({'projectId': project_id}).to_list(length=None)
    for job in jobs:
        _remove_id_field(job)
    jobs = [ProtocaasJob(**job) for job in jobs] # validate jobs
    if not include_private_keys:
        for job in jobs:
            job.jobPrivateKey = '' # hide the private key
    for job in jobs:
        job.dandiApiKey = None # hide the DANDI API key
    return jobs

async def update_project(project_id: str, update: dict):
    client = _get_mongo_client()
    projects_collection = client['protocaas']['projects']
    await projects_collection.update_one({
        'projectId': project_id
    }, {
        '$set': update
    })

async def delete_project(project_id: str):
    client = _get_mongo_client()
    projects_collection = client['protocaas']['projects']
    await projects_collection.delete_one({
        'projectId': project_id
    })

async def delete_all_files_in_project(project_id: str):
    client = _get_mongo_client()
    files_collection = client['protocaas']['files']
    await files_collection.delete_many({
        'projectId': project_id
    })

async def delete_all_jobs_in_project(project_id: str):
    client = _get_mongo_client()
    jobs_collection = client['protocaas']['jobs']
    await jobs_collection.delete_many({
        'projectId': project_id
    })

async def insert_project(project: ProtocaasProject):
    client = _get_mongo_client()
    projects_collection = client['protocaas']['projects']
    await projects_collection.insert_one(project.dict(exclude_none=True))

async def fetch_compute_resource(compute_resource_id: str):
    client = _get_mongo_client()
    compute_resources_collection = client['protocaas']['computeResources']
    compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
    if compute_resource is None:
        return None
    _remove_id_field(compute_resource)
    compute_resource = ProtocaasComputeResource(**compute_resource) # validate compute resource
    return compute_resource

async def fetch_compute_resources_for_user(user_id: str):
    client = _get_mongo_client()
    compute_resources_collection = client['protocaas']['computeResources']
    compute_resources = await compute_resources_collection.find({'ownerId': user_id}).to_list(length=None)
    for compute_resource in compute_resources:
        _remove_id_field(compute_resource)
    compute_resources = [ProtocaasComputeResource(**compute_resource) for compute_resource in compute_resources] # validate compute resources
    return compute_resources

async def update_compute_resource(compute_resource_id: str, update: dict):
    client = _get_mongo_client()
    compute_resources_collection = client['protocaas']['computeResources']
    await compute_resources_collection.update_one({
        'computeResourceId': compute_resource_id
    }, {
        '$set': update
    })

async def delete_compute_resource(compute_resource_id: str):
    client = _get_mongo_client()
    compute_resources_collection = client['protocaas']['computeResources']
    await compute_resources_collection.delete_one({
        'computeResourceId': compute_resource_id
    })

async def register_compute_resource(compute_resource_id: str, name: str, user_id: str):
    client = _get_mongo_client()
    compute_resources_collection = client['protocaas']['computeResources']

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
        compute_resources_collection.insert_one(new_compute_resource.dict(exclude_none=True))

async def fetch_compute_resource_jobs(compute_resource_id: str, statuses: Union[List[str], None], include_private_keys: bool) -> List[ProtocaasJob]:
    client = _get_mongo_client()
    jobs_collection = client['protocaas']['jobs']
    if statuses is not None:
        jobs = await jobs_collection.find({
            'computeResourceId': compute_resource_id,
            'status': {'$in': statuses}
        }).to_list(length=None)
    else:
        jobs = await jobs_collection.find({
            'computeResourceId': compute_resource_id
        }).to_list(length=None)
    for job in jobs:
        _remove_id_field(job)
    jobs = [ProtocaasJob(**job) for job in jobs] # validate jobs
    if not include_private_keys:
        for job in jobs:
            job.jobPrivateKey = '' # hide the private key
    for job in jobs:
        job.dandiApiKey = None # hide the DANDI API key
    return jobs

async def update_compute_resource_node(compute_resource_id: str, compute_resource_node_id: str, compute_resource_node_name: str):
    client = _get_mongo_client()
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

async def set_compute_resource_spec(compute_resource_id: str, spec: ComputeResourceSpec):
    client = _get_mongo_client()
    compute_resources_collection = client['protocaas']['computeResources']
    compute_resource = await compute_resources_collection.find_one({'computeResourceId': compute_resource_id})
    if compute_resource is None:
        raise Exception(f"No compute resource with ID {compute_resource_id}")
    await compute_resources_collection.update_one({'computeResourceId': compute_resource_id}, {
        '$set': {
            'spec': spec.dict(exclude_none=True)
        }
    })

async def fetch_job(job_id: str, *, include_dandi_api_key: bool=False):
    client = _get_mongo_client()
    jobs_collection = client['protocaas']['jobs']
    job = await jobs_collection.find_one({'jobId': job_id})
    _remove_id_field(job)
    if job is None:
        return None
    job = ProtocaasJob(**job) # validate job
    if not include_dandi_api_key:
        job.dandiApiKey = None
    return job

async def update_job(job_id: str, update: dict):
    client = _get_mongo_client()
    jobs_collection = client['protocaas']['jobs']
    await jobs_collection.update_one({
        'jobId': job_id
    }, {
        '$set': update
    })

async def delete_job(job_id: str):
    client = _get_mongo_client()
    jobs_collection = client['protocaas']['jobs']
    await jobs_collection.delete_one({
        'jobId': job_id
    })

async def insert_job(job: ProtocaasJob):
    client = _get_mongo_client()
    jobs_collection = client['protocaas']['jobs']
    await jobs_collection.insert_one(job.dict(exclude_none=True))

async def fetch_file(project_id: str, file_name: str):
    client = _get_mongo_client()
    files_collection = client['protocaas']['files']
    file = await files_collection.find_one({
        'projectId': project_id,
        'fileName': file_name
    })
    _remove_id_field(file)
    if file is None:
        return None
    file = ProtocaasFile(**file) # validate file
    return file

async def delete_file(project_id: str, file_name: str):
    client = _get_mongo_client()
    files_collection = client['protocaas']['files']
    await files_collection.delete_one({
        'projectId': project_id,
        'fileName': file_name
    })

async def insert_file(file: ProtocaasFile):
    client = _get_mongo_client()
    files_collection = client['protocaas']['files']
    await files_collection.insert_one(file.dict(exclude_none=True))