from typing import Union, List, Any
from pydantic import BaseModel

class ProtocaasWorkspaceUser(BaseModel):
    userId: str
    role: str # 'admin' | 'editor' | 'viewer'

class ProtocaasWorkspace(BaseModel):
    workspaceId: str
    ownerId: str
    name: str
    description: str
    users: List[ProtocaasWorkspaceUser]
    publiclyReadable: bool
    listed: bool
    timestampCreated: float
    timestampModified: float
    computeResourceId: Union[str, None]=None

class ProtocaasProject(BaseModel):
    projectId: str
    workspaceId: str
    name: str
    description: str
    timestampCreated: float
    timestampModified: float

class ProtocaasJobInputFile(BaseModel):
    name: str
    fileId: str
    fileName: str

class ProtocaasJobInputParameter(BaseModel):
    name: str
    value: Union[Any, None]=None

class ProtocaasJobOutputFile(BaseModel):
    name: str
    fileName: str
    fileId: Union[str, None]=None

class ComputeResourceSpecProcessorParameter(BaseModel):
    name: str
    help: str
    type: str
    default: Union[Any, None]=None
    options: Union[List[str], List[int], None]=None

class ComputeResourceSpecProcessorInput(BaseModel):
    name: str
    help: str

class ComputeResourceSpecProcessorOutput(BaseModel):
    name: str
    help: str

class ComputeResourceSpecProcessorAttribute(BaseModel):
    name: str
    value: Any

class ComputeResourceSpecProcessorTag(BaseModel):
    tag: str

class ComputeResourceSpecProcessor(BaseModel):
    name: str
    help: str
    inputs: List[ComputeResourceSpecProcessorInput]
    outputs: List[ComputeResourceSpecProcessorOutput]
    parameters: List[ComputeResourceSpecProcessorParameter]
    attributes: List[ComputeResourceSpecProcessorAttribute]
    tags: List[ComputeResourceSpecProcessorTag]

class ProtocaasJob(BaseModel):
    projectId: str
    workspaceId: str
    jobId: str
    jobPrivateKey: str
    userId: str
    processorName: str
    batchId: Union[str, None]=None
    inputFiles: List[ProtocaasJobInputFile]
    inputFileIds: List[str]
    inputParameters: List[ProtocaasJobInputParameter]
    outputFiles: List[ProtocaasJobOutputFile]
    timestampCreated: float
    computeResourceId: str
    status: str # 'pending' | 'queued' | 'starting' | 'running' | 'completed' | 'failed'
    error: Union[str, None]=None
    processVersion: Union[str, None]=None
    computeResourceNodeId: Union[str, None]=None
    computeResourceNodeName: Union[str, None]=None
    consoleOutput: Union[str, None]=None
    timestampQueued: Union[float, None]=None
    timestampStarting: Union[float, None]=None
    timestampStarted: Union[float, None]=None
    timestampFinished: Union[float, None]=None
    outputFileIds: Union[List[str], None]=None
    processorSpec: ComputeResourceSpecProcessor

class ProtocaasFile(BaseModel):
    projectId: str
    workspaceId: str
    fileId: str
    userId: str
    fileName: str
    size: int
    timestampCreated: float
    content: str
    metadata: dict
    jobId: Union[str, None]=None

class ComputeResourceAwsBatchOpts(BaseModel):
    jobQueue: str
    jobDefinition: str

class ComputeResourceSlurmOpts(BaseModel):
    partition: Union[str, None]=None
    time: Union[str, None]=None
    cpusPerTask: Union[int, None]=None
    otherOpts: Union[str, None]=None

class ProtocaasComputeResourceApp(BaseModel):
    name: str
    executablePath: str
    container: Union[str, None]=None
    awsBatch: Union[ComputeResourceAwsBatchOpts, None]=None
    slurm: Union[ComputeResourceSlurmOpts, None]=None

class ProtocaasComputeResource(BaseModel):
    computeResourceId: str
    ownerId: str
    name: str
    timestampCreated: float
    apps: List[ProtocaasComputeResourceApp]
    spec: Union[dict, None]=None

class ComputeResourceSpecApp(BaseModel):
    name: str
    help: str
    processors: List[ComputeResourceSpecProcessor]

class ComputeResourceSpec(BaseModel):
    apps: List[ComputeResourceSpecApp]

class PubsubSubscription(BaseModel):
    pubnubSubscribeKey: str
    pubnubChannel: str
    pubnubUser: str

class ProcessorGetJobResponseInput(BaseModel):
    name: str
    url: str

class ProcessorGetJobResponseOutput(BaseModel):
    name: str

class ProcessorGetJobResponseParameter(BaseModel):
    name: str
    value: Any

class ProcessorGetJobResponse(BaseModel):
    jobId: str
    status: str
    processorName: str
    inputs: List[ProcessorGetJobResponseInput]
    outputs: List[ProcessorGetJobResponseOutput]
    parameters: List[ProcessorGetJobResponseParameter]