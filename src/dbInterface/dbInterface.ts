import { getAuthorizationHeaderForUrl } from "../pages/ProjectPage/FileEditor/NwbFileEditor";
import { ComputeResourceAwsBatchOpts, ComputeResourceSlurmOpts, ComputeResourceSpecProcessor, ProtocaasComputeResource, ProtocaasFile, ProtocaasJob, ProtocaasProject, ProtocaasWorkspace } from "../types/protocaas-types";

type Auth = {
    githubAccessToken?: string
}

export const getRequest = async (url: string, auth: Auth): Promise<any> => {
    const response = await fetch(url, {
        headers: {
            'github-access-token': auth.githubAccessToken || ''
        }
    })
    if (response.status !== 200) {
        throw Error(`Unable to fetch ${url}: ${response.status}`)
    }
    const json = await response.json()
    return json
}

export const postRequest = async (url: string, body: any, auth: Auth): Promise<any> => {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'github-access-token': auth.githubAccessToken || ''
        },
        body: JSON.stringify(body)
    })
    if (response.status !== 200) {
        throw Error(`Unable to POST ${url}: ${response.status}`)
    }
    const json = await response.json()
    return json
}

export const putRequest = async (url: string, body: any, auth: Auth): Promise<any> => {
    const response = await fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'github-access-token': auth.githubAccessToken || ''
        },
        body: JSON.stringify(body)
    })
    if (response.status !== 200) {
        throw Error(`Unable to PUT ${url}: ${response.status}`)
    }
    const json = await response.json()
    return json
}

export const deleteRequest = async (url: string, auth: Auth): Promise<any> => {
    const response = await fetch(url, {
        method: 'DELETE',
        headers: {
            'github-access-token': auth.githubAccessToken || ''
        }
    })
    if (response.status !== 200) {
        throw Error(`Unable to DELETE ${url}: ${response.status}`)
    }
    const json = await response.json()
    return json
}

export const fetchWorkspaces = async (auth: Auth): Promise<ProtocaasWorkspace[]> => {
    const resp = await getRequest('/api/gui/workspaces', auth)
    return resp.workspaces
}

export const fetchWorkspace = async (workspaceId: string, auth: Auth): Promise<ProtocaasWorkspace | undefined> => {
    const resp = await getRequest(`/api/gui/workspaces/${workspaceId}`, auth)
    return resp.workspace
}

export const createWorkspace = async (workspaceName: string, auth: Auth): Promise<string> => {
    const url = `/api/gui/workspaces`
    const response = await postRequest(url, {name: workspaceName}, auth)
    return response.workspaceId
}

export const fetchProjects = async (workspaceId: string, auth: Auth): Promise<ProtocaasProject[]> => {
    const url = `/api/gui/workspaces/${workspaceId}/projects`
    const response = await getRequest(url, auth)
    if (!response.success) throw Error(`Error in fetchProjects: ${response.error}`)
    return response.projects
}

export const createProject = async (workspaceId: string, projectName: string, auth: Auth): Promise<string> => {
    const url = `/api/gui/projects`
    const response = await postRequest(url, {name: projectName, workspaceId}, auth)
    if (!response.success) throw Error(`Error in createProject: ${response.error}`)
    return response.projectId
}

export const setWorkspaceUsers = async (workspaceId: string, users: {userId: string, role: 'admin' | 'editor' | 'viewer'}[], auth: Auth): Promise<void> => {
    const url = `/api/gui/workspaces/${workspaceId}/users`
    const response = await putRequest(url, {users}, auth)
    if (!response.success) throw Error(`Error in setWorkspaceUsers: ${response.error}`)
}

export const setWorkspaceName = async (workspaceId: string, name: string, auth: Auth): Promise<void> => {
    const url = `/api/gui/workspaces/${workspaceId}/name`
    const response = await putRequest(url, {name}, auth)
    if (!response.success) throw Error(`Error in setWorkspaceName: ${response.error}`)
}

export const setWorkspacePubliclyReadable = async (workspaceId: string, publiclyReadable: boolean, auth: Auth): Promise<void> => {
    const url = `/api/gui/workspaces/${workspaceId}/publicly_readable`
    const response = await putRequest(url, {publiclyReadable}, auth)
    if (!response.success) throw Error(`Error in setWorkspacePubliclyReadable: ${response.error}`)
}

export const setWorkspaceListed = async (workspaceId: string, listed: boolean, auth: Auth): Promise<void> => {
    const url = `/api/gui/workspaces/${workspaceId}/listed`
    const response = await putRequest(url, {listed}, auth)
    if (!response.success) throw Error(`Error in setWorkspaceListed: ${response.error}`)
}

export const setWorkspaceComputeResourceId = async (workspaceId: string, computeResourceId: string, auth: Auth): Promise<void> => {
    const url = `/api/gui/workspaces/${workspaceId}/compute_resource_id`
    const response = await putRequest(url, {computeResourceId}, auth)
    if (!response.success) throw Error(`Error in setWorkspaceComputeResourceId: ${response.error}`)
}

export const deleteWorkspace = async (workspaceId: string, auth: Auth): Promise<void> => {
    const url = `/api/gui/workspaces/${workspaceId}`
    const resp = await deleteRequest(url, auth)
    if (!resp.success) throw Error(`Error in deleteWorkspace: ${resp.error}`)
}

export const fetchProject = async (projectId: string, auth: Auth): Promise<ProtocaasProject | undefined> => {
    const url = `/api/gui/projects/${projectId}`
    const response = await getRequest(url, auth)
    if (!response.success) throw Error(`Error in fetchProject: ${response.error}`)
    return response.project
}

export const fetchFiles = async (projectId: string, auth: Auth): Promise<ProtocaasFile[]> => {
    const url = `/api/gui/projects/${projectId}/files`
    const response = await getRequest(url, auth)
    if (!response.success) throw Error(`Error in fetchFiles: ${response.error}`)
    return response.files
}

export const fetchFile = async (projectId: string, fileName: string, auth: Auth): Promise<ProtocaasFile | undefined> => {
    const url = `/api/gui/projects/${projectId}/files/${fileName}`
    const response = await getRequest(url, auth)
    if (!response.success) throw Error(`Error in fetchFile: ${response.error}`)
    return response.file
}

const headRequest = async (url: string, headers?: any) => {
    // Cannot use HEAD, because it is not allowed by CORS on DANDI AWS bucket
    // let headResponse
    // try {
    //     headResponse = await fetch(url, {method: 'HEAD'})
    //     if (headResponse.status !== 200) {
    //         return undefined
    //     }
    // }
    // catch(err: any) {
    //     console.warn(`Unable to HEAD ${url}: ${err.message}`)
    //     return undefined
    // }
    // return headResponse

    // Instead, use aborted GET.
    const controller = new AbortController();
    const signal = controller.signal;
    const response = await fetch(url, {
        signal,
        headers
    })
    controller.abort();
    return response
}

const getSizeForRemoteFile = async (url: string): Promise<number> => {
    const authorizationHeader = getAuthorizationHeaderForUrl(url)
    const headers = authorizationHeader ? {Authorization: authorizationHeader} : undefined
    const response = await headRequest(url, headers)
    if (!response) {
        throw Error(`Unable to HEAD ${url}`)
    }
    if ((response.redirected === true) && (response.status !== 200)) {
        // this is tricky -- there is a CORS problem which prevents the content-length from being on the redirected response
        if (url === response.url) {
            // to be safe, let's make sure we are not in an infinite loop
            throw Error(`Unable to HEAD ${url} -- infinite redirect`)
        }
        return await getSizeForRemoteFile(response.url)
    }
    const size = Number(response.headers.get('content-length'))
    if (isNaN(size)) {
        throw Error(`Unable to get content-length for ${url}`)
    }
    return size
}

export const setUrlFile = async (projectId: string, fileName: string, url: string, metadata: any, auth: Auth): Promise<void> => {
    const reqUrl = `/api/gui/projects/${projectId}/files/${fileName}`
    const size = await getSizeForRemoteFile(url)
    const body = {
        content: `url:${url}`,
        size,
        metadata
    }
    const response = await putRequest(reqUrl, body, auth)
    if (!response.success) throw Error(`Error in setUrlFile: ${response.error}`)
}

export const deleteFile = async (workspaceId: string, projectId: string, fileName: string, auth: Auth): Promise<void> => {
    const url = `/api/gui/projects/${projectId}/files/${fileName}`
    const resp = await deleteRequest(url, auth)
    if (!resp.success) throw Error(`Error in deleteFile: ${resp.error}`)
}

export const deleteProject = async (projectId: string, auth: Auth): Promise<void> => {
    const url = `/api/gui/projects/${projectId}`
    const resp = await deleteRequest(url, auth)
    if (!resp.success) throw Error(`Error in deleteProject: ${resp.error}`)
}

export const setProjectName = async (projectId: string, name: string, auth: Auth): Promise<void> => {
    const url = `/api/gui/projects/${projectId}/name`
    const response = await putRequest(url, {name}, auth)
    if (!response.success) throw Error(`Error in setProjectName: ${response.error}`)
}

export const fetchComputeResources = async (auth: Auth): Promise<ProtocaasComputeResource[]> => {
    const url = `/api/gui/compute_resources`
    const response = await getRequest(url, auth)
    if (!response.success) throw Error(`Error in fetchComputeResources: ${response.error}`)
    return response.computeResources
}

export const fetchComputeResource = async (computeResourceId: string, auth: Auth): Promise<ProtocaasComputeResource | undefined> => {
    const url = `/api/gui/compute_resources/${computeResourceId}`
    const response = await getRequest(url, auth)
    if (!response.success) throw Error(`Error in fetchComputeResource: ${response.error}`)
    return response.computeResource
}

export const registerComputeResource = async (computeResourceId: string, resourceCode: string, name: string, auth: Auth): Promise<void> => {
    const url = `/api/gui/compute_resources/register`
    const response = await postRequest(url, {computeResourceId, resourceCode, name}, auth)
    if (!response.success) throw Error(`Error in registerComputeResource: ${response.error}`)
}

export const deleteComputeResource = async (computeResourceId: string, auth: Auth): Promise<void> => {
    const url = `/api/gui/compute_resources/${computeResourceId}`
    const resp = await deleteRequest(url, auth)
    if (!resp.success) throw Error(`Error in deleteComputeResource: ${resp.error}`)
}

export type App = {
    name: string
    executablePath: string
    container?: string
    awsBatch?: ComputeResourceAwsBatchOpts
    slurm?: ComputeResourceSlurmOpts
}

export const setComputeResourceApps = async (computeResourceId: string, apps: App[], auth: Auth): Promise<void> => {
    const url = `/api/gui/compute_resources/${computeResourceId}/apps`
    const response = await putRequest(url, {apps}, auth)
    if (!response.success) throw Error(`Error in setComputeResourceApps: ${response.error}`)
}

export type ProtocaasProcessingJobDefinition = {
    processorName: string,
    inputFiles: {
        name: string
        fileName: string
    }[],
    inputParameters: {
        name: string
        value: any
    }[],
    outputFiles: {
        name: string
        fileName: string
    }[]
}

export type ProtocaasProcessingJobDefinitionAction = {
    type: 'setInputFile'
    name: string
    fileName: string
} | {
    type: 'setInputParameter'
    name: string
    value: any
} | {
    type: 'setOutputFile'
    name: string
    fileName: string
} | {
    type: 'setProcessorName'
    processorName: string
} | {
    type: 'setJobDefinition'
    jobDefinition: ProtocaasProcessingJobDefinition
}

export const defaultJobDefinition: ProtocaasProcessingJobDefinition = {
    processorName: '',
    inputFiles: [],
    inputParameters: [],
    outputFiles: []
}

export const protocaasJobDefinitionReducer = (state: ProtocaasProcessingJobDefinition, action: ProtocaasProcessingJobDefinitionAction): ProtocaasProcessingJobDefinition => {

    switch (action.type) {
        case 'setInputFile':
            // check if no change
            if (state.inputFiles.find(f => f.name === action.name && f.fileName === action.fileName)) {
                return state
            }
            return {
                ...state,
                inputFiles: state.inputFiles.map(f => f.name === action.name ? {...f, fileName: action.fileName} : f)
            }
        case 'setInputParameter':
            // check if no change
            if (state.inputParameters.find(p => p.name === action.name && deepEqual(p.value, action.value))) {
                return state
            }
            return {
                ...state,
                inputParameters: state.inputParameters.map(p => p.name === action.name ? {...p, value: action.value} : p)
            }
        case 'setOutputFile':
            // check if no change
            if (state.outputFiles.find(f => f.name === action.name && f.fileName === action.fileName)) {
                return state
            }
            return {
                ...state,
                outputFiles: state.outputFiles.map(f => f.name === action.name ? {...f, fileName: action.fileName} : f)
            }
        case 'setProcessorName':
            // check if no change
            if (state.processorName === action.processorName) {
                return state
            }
            return {
                ...state,
                processorName: action.processorName
            }
        case 'setJobDefinition':
            return action.jobDefinition
        default:
            throw Error(`Unexpected action type ${(action as any).type}`)
    }
}

export const createJob = async (
    a: {
        workspaceId: string,
        projectId: string,
        jobDefinition: ProtocaasProcessingJobDefinition,
        processorSpec: ComputeResourceSpecProcessor,
        files: ProtocaasFile[],
        batchId?: string
    },
    auth: Auth
) : Promise<string> => {
    const {workspaceId, projectId, jobDefinition, processorSpec, files, batchId} = a
    const processorName = jobDefinition.processorName
    const inputFiles = jobDefinition.inputFiles
    const inputParameters = jobDefinition.inputParameters
    const outputFiles = jobDefinition.outputFiles
    const url = `/api/gui/jobs`
    let needToSendDandiApiKey = false
    let needToSendDandiStagingApiKey = false
    for (const inputFile of inputFiles) {
        const ff = files.find(f => f.fileName === inputFile.fileName)
        if (ff) {
            if (ff.content.startsWith('url:')) {
                const url = ff.content.slice('url:'.length)
                if (url.startsWith('https://api.dandiarchive.org/api/')) {
                    needToSendDandiApiKey = true
                }
                if (url.startsWith('https://api-staging.dandiarchive.org/api/')) {
                    needToSendDandiStagingApiKey = true
                }
            }
        }
    }
    let dandiApiKey: string | undefined = undefined
    if (needToSendDandiApiKey) {
        dandiApiKey = localStorage.getItem('dandiApiKey') || undefined
    }
    else if (needToSendDandiStagingApiKey) {
        dandiApiKey = localStorage.getItem('dandiStagingApiKey') || undefined
    }
    const body: {[key: string]: any} = {
        workspaceId,
        projectId,
        processorName,
        inputFiles,
        inputParameters,
        outputFiles,
        processorSpec,
        batchId
    }
    if (dandiApiKey) {
        body.dandiApiKey = dandiApiKey
    }
    const response = await postRequest(url, body, auth)
    if (!response.success) throw Error(`Error in createJob: ${response.error}`)
    return response.jobId
}

export const deleteJob = async (jobId: string, auth: Auth): Promise<void> => {
    const url = `/api/gui/jobs/${jobId}`
    const resp = await deleteRequest(url, auth)
    if (!resp.success) throw Error(`Error in deleteJob: ${resp.error}`)
}

export const fetchJobsForProject = async (projectId: string, auth: Auth): Promise<ProtocaasJob[]> => {
    const url = `/api/gui/projects/${projectId}/jobs`
    const response = await getRequest(url, auth)
    if (!response.success) throw Error(`Error in fetchJobsForProject: ${response.error}`)
    return response.jobs
}

export const fetchJobsForComputeResource = async (computeResourceId: string, auth: Auth): Promise<ProtocaasJob[]> => {
    const url = `/api/gui/compute_resources/${computeResourceId}/jobs`
    const response = await getRequest(url, auth)
    if (!response.success) throw Error(`Error in fetchJobsForComputeResource: ${response.error}`)
    return response.jobs
}

export const fetchJob = async (jobId: string, auth: Auth): Promise<ProtocaasJob | undefined> => {
    const url = `/api/gui/jobs/${jobId}`
    const response = await getRequest(url, auth)
    if (!response.success) throw Error(`Error in fetchJob: ${response.error}`)
    return response.job
}

export const getComputeResource = async (computeResourceId: string): Promise<any> => {
    const url = `/api/gui/compute_resources/${computeResourceId}`
    const response = await getRequest(url, {})
    if (!response.success) throw Error(`Error in getComputeResource: ${response.error}`)
    return response.computeResource
}

const deepEqual = (a: any, b: any): boolean => {
    if (typeof a !== typeof b) {
        return false
    }
    if (typeof a === 'object') {
        if (Array.isArray(a)) {
            if (!Array.isArray(b)) {
                return false
            }
            if (a.length !== b.length) {
                return false
            }
            for (let i = 0; i < a.length; i++) {
                if (!deepEqual(a[i], b[i])) {
                    return false
                }
            }
            return true
        }
        else {
            const aKeys = Object.keys(a)
            const bKeys = Object.keys(b)
            if (aKeys.length !== bKeys.length) {
                return false
            }
            for (const key of aKeys) {
                if (!deepEqual(a[key], b[key])) {
                    return false
                }
            }
            return true
        }
    }
    else {
        return a === b
    }
}