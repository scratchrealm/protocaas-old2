from typing import List
from ..sdk._post_api_request import _post_api_request


class Project:
    def __init__(self, project_data: dict, files_data: List[dict], jobs_data: List[dict]) -> None:
        self._project_id = project_data['projectId']
        self._workspace_id = project_data['workspaceId']
        self._name = project_data['name']
        self._description = project_data['description']
        self._timestamp_created = project_data['timestampCreated']
        self._timestamp_modified = project_data['timestampModified']

        self._files = [
            ProjectFile(f)
            for f in files_data
        ]

        self._jobs = [
            ProjectJob(j)
            for j in jobs_data
        ]
    def get_file(self, file_name: str) -> 'ProjectFile':
        for f in self._files:
            if f._file_name == file_name:
                return f
        raise Exception(f'File not found: {file_name}')

class ProjectFile:
    def __init__(self, file_data: dict) -> None:
        self._project_id = file_data['projectId']
        self._workspace_id = file_data['workspaceId']
        self._file_id = file_data['fileId']
        self._user_id = file_data['userId']
        self._file_name = file_data['fileName']
        self._size = file_data['size']
        self._timestamp_created = file_data['timestampCreated']
        self._content = file_data['content']
        self._metadata = file_data['metadata']
        self._job_id = file_data.get('jobId', None)
    def get_url(self) -> str:
        a = self._content
        if not a.startswith('url:'):
            raise Exception(f'Unexpected content for file {self._file_name}: {a}')
        return a[len('url:'):]

class ProjectFolder:
    def __init__(self, project: Project, path: str) -> None:
        self._project = project
        self._path = path
    def get_files(self) -> List[ProjectFile]:
        ret: List[ProjectFile] = []
        for f in self._project._files:
            a = f._file_name.split('/')
            ok = False
            if len(a) <= 1:
                ok = (self._path == '')
            else:
                ok = '/'.join(a[:-1]) == self._path
            if ok:
                ret.append(f)
        return ret
    def get_folders(self) -> List['ProjectFolder']:
        folder_paths = set()
        for f in self._project._files:
            a = f._file_name.split('/')
            if len(a) <= 1:
                continue
            parent_path = '/'.join(a[:-1])
            b = parent_path.split('/')
            ok = False
            if len(b) <= 1:
                ok = (self._path == '')
            else:
                ok = '/'.join(b[:-1]) == self._path
            if ok:
                folder_paths.add(parent_path)
        sorted_folder_paths = sorted(list(folder_paths))
        return [
            ProjectFolder(self._project, p)
            for p in sorted_folder_paths
        ]

class ProjectJob:
    def __init__(self, job_data: dict) -> None:
        self._project_id = job_data['projectId']
        self._workspace_id = job_data['workspaceId']
        self._job_id = job_data['jobId']
        self._job_private_key = job_data['jobPrivateKey']
        self._user_id = job_data['userId']
        self._processor_name = job_data['processorName']
        self._batch_id = job_data.get('batchId', None)
        self._input_files = job_data['inputFiles']
        self._input_file_ids = job_data['inputFileIds']
        self._input_parameters = job_data['inputParameters']
        self._output_files = job_data['outputFiles']
        self._timestamp_created = job_data['timestampCreated']
        self._compute_resource_id = job_data['computeResourceId']
        self._status = job_data['status']
        self._error = job_data.get('error', None)
        self._process_version = job_data.get('processVersion', None)
        self._compute_resource_node_id = job_data.get('computeResourceNodeId', None)
        self._compute_resource_node_name = job_data.get('computeResourceNodeName', None)
        self._console_output = job_data.get('consoleOutput', None)
        self._timestamp_queued = job_data.get('timestampQueued', None)
        self._timestamp_starting = job_data.get('timestampStarting', None)
        self._timestamp_started = job_data.get('timestampStarted', None)
        self._timestamp_finished = job_data.get('timestampFinished', None)
        self._output_file_ids = job_data.get('outputFileIds', None)
        self._processor_spec = job_data['processorSpec']

def load_project(project_id: str) -> Project:
    req = {
        'type': 'client.loadProject',
        'projectId': project_id
    }
    resp = _post_api_request(req)
    project_data = resp['project']
    files_data = resp['files']
    jobs_data = resp['jobs']
    return Project(project_data, files_data, jobs_data)

# type ProtocaasProject = {
#     projectId: string
#     workspaceId: string
#     name: string
#     description: string
#     timestampCreated: number
#     timestampModified: number
# }

# type ProtocaasFile = {
#     projectId: string
#     workspaceId: string
#     fileId: string
#     userId: string
#     fileName: string
#     size: number
#     timestampCreated: number
#     content: string
#     metadata: {
#         [key: string]: any
#     }
#     jobId?: string
# }

# type ProtocaasJob = {
#     projectId: string
#     workspaceId: string
#     jobId: string
#     jobPrivateKey: string
#     userId: string
#     processorName: string
#     batchId?: string
#     inputFiles: {
#         name: string
#         fileId: string
#         fileName: string
#     }[]
#     inputFileIds: string[]
#     inputParameters: {
#         name: string
#         value?: any
#     }[]
#     outputFiles: {
#         name: string
#         fileName: string
#         fileId?: string
#     }[]
#     timestampCreated: number
#     computeResourceId: string
#     status: 'pending' | 'queued' | 'starting' | 'running' | 'completed' | 'failed'
#     error?: string
#     processVersion?: string
#     computeResourceNodeId?: string
#     computeResourceNodeName?: string
#     consoleOutput?: string
#     timestampQueued?: number
#     timestampStarting?: number
#     timestampStarted?: number
#     timestampFinished?: number
#     outputFileIds?: string[]
#     processorSpec: ComputeResourceSpecProcessor
# }