import React, { FunctionComponent, PropsWithChildren, useCallback, useEffect, useMemo } from 'react';
import { deleteFile, deleteJob, deleteProject, fetchFiles, fetchJobsForProject, fetchProject, setProjectName } from '../../dbInterface/dbInterface';
import { useGithubAuth } from '../../GithubAuth/useGithubAuth';
import { onPubsubMessage } from '../../pubnub/pubnub';
import { ProtocaasFile, ProtocaasJob, ProtocaasProject } from '../../types/protocaas-types';

type Props = {
    projectId: string
}

type OpenTabsState = {
    openTabs: {
        tabName: string
        content?: string
        editedContent?: string
    }[]
    currentTabName?: string
}

type OpenTabsAction = {
    type: 'openTab'
    tabName: string
} | {
    type: 'setTabContent'
    tabName: string
    content: string | undefined // undefined triggers a reload
} | {
    type: 'setTabEditedContent'
    tabName: string
    editedContent: string
} | {
    type: 'closeTab'
    tabName: string
} | {
    type: 'closeAllTabs'
} | {
    type: 'setCurrentTab'
    tabName: string
}

const openTabsReducer = (state: OpenTabsState, action: OpenTabsAction) => {
    switch (action.type) {
        case 'openTab':
            if (state.openTabs.find(x => x.tabName === action.tabName)) {
                return {
                    ...state,
                    currentTabName: action.tabName
                }
            }
            return {
                ...state,
                openTabs: [...state.openTabs, {tabName: action.tabName}],
                currentTabName: action.tabName
            }
        case 'setTabContent':
            return {
                ...state,
                openTabs: state.openTabs.map(x => {
                    if (x.tabName === action.tabName) {
                        return {
                            ...x,
                            content: action.content
                        }
                    }
                    return x
                })
            }
        case 'setTabEditedContent':
            return {
                ...state,
                openTabs: state.openTabs.map(x => {
                    if (x.tabName === action.tabName) {
                        return {
                            ...x,
                            editedContent: action.editedContent
                        }
                    }
                    return x
                })
            }
        case 'closeTab':
            if (!state.openTabs.find(x => x.tabName === action.tabName)) {
                return state
            }
            return {
                ...state,
                openTabs: state.openTabs.filter(x => x.tabName !== action.tabName),
                currentTabName: state.currentTabName === action.tabName ? state.openTabs[0]?.tabName : state.currentTabName
            }
        case 'closeAllTabs':
            return {
                ...state,
                openTabs: [],
                currentTabName: undefined
            }
        case 'setCurrentTab':
            if (!state.openTabs.find(x => x.tabName === action.tabName)) {
                return state
            }
            return {
                ...state,
                currentTabName: action.tabName
            }
    }
}

type ProjectPageContextType = {
    projectId: string
    workspaceId: string
    project?: ProtocaasProject
    files?: ProtocaasFile[]
    filesIncludingPending?: ProtocaasFile[]
    openTabs: {
        tabName: string
        content?: string
        editedContent?: string
    }[]
    currentTabName?: string
    jobs?: ProtocaasJob[]
    openTab: (tabName: string) => void
    closeTab: (tabName: string) => void
    closeAllTabs: () => void
    setCurrentTab: (tabName: string) => void
    setTabContent: (tabName: string, content: string | undefined) => void
    setTabEditedContent: (tabName: string, editedContent: string) => void
    refreshFiles: () => void
    deleteProject: () => Promise<void>
    setProjectName: (name: string) => void
    deleteJob: (jobId: string) => Promise<void>
    refreshJobs: () => void
    deleteFile: (fileName: string) => Promise<void>
    fileHasBeenEdited: (fileName: string) => boolean
}

const ProjectPageContext = React.createContext<ProjectPageContextType>({
    projectId: '',
    workspaceId: '',
    openTabs: [],
    currentTabName: undefined,
    openTab: () => {},
    closeTab: () => {},
    closeAllTabs: () => {},
    setCurrentTab: () => {},
    setTabContent: () => {},
    setTabEditedContent: () => {},
    refreshFiles: () => {},
    deleteProject: async () => {},
    setProjectName: () => {},
    deleteJob: async () => {},
    refreshJobs: () => {},
    deleteFile: async () => {},
    fileHasBeenEdited: () => false
})

export const SetupProjectPage: FunctionComponent<PropsWithChildren<Props>> = ({children, projectId}) => {
    const [project, setProject] = React.useState<ProtocaasProject | undefined>()
    const [files, setFiles] = React.useState<ProtocaasFile[] | undefined>()
    const [refreshFilesCode, setRefreshFilesCode] = React.useState(0)
    const refreshFiles = useCallback(() => setRefreshFilesCode(rfc => rfc + 1), [])

    const [jobs, setJobs] = React.useState<ProtocaasJob[] | undefined>(undefined)
    const [refreshJobsCode, setRefreshJobsCode] = React.useState(0)
    const refreshJobs = useCallback(() => setRefreshJobsCode(c => c + 1), [])

    const [refreshProjectCode, setRefreshProjectCode] = React.useState(0)
    const refreshProject = useCallback(() => setRefreshProjectCode(rac => rac + 1), [])

    const [openTabs, openTabsDispatch] = React.useReducer(openTabsReducer, {openTabs: [], currentTabName: undefined})

    const {accessToken, userId} = useGithubAuth()
    const auth = useMemo(() => (accessToken ? {githubAccessToken: accessToken, userId} : {}), [accessToken, userId])

    useEffect(() => {
        (async () => {
            setProject(undefined)
            if (!projectId) return
            const project = await fetchProject(projectId, auth)
            setProject(project)
        })()
    }, [projectId, auth, refreshProjectCode])

    useEffect(() => {
        (async () => {
            setFiles(undefined)
            if (!projectId) return
            const af = await fetchFiles(projectId, auth)
            setFiles(af)
        })()
    }, [refreshFilesCode, projectId, auth])

    useEffect(() => {
        let canceled = false
        ;(async () => {
            setJobs(undefined)
            if (!projectId) return
            const x = await fetchJobsForProject(projectId, auth)
            if (canceled) return
            setJobs(x)
        })()
        return () => {canceled = true}
    }, [refreshJobsCode, projectId, auth])

    // if any jobs are newly completed, refresh the files
    const [previousJobs, setPreviousJobs] = React.useState<ProtocaasJob[] | undefined>(undefined)
    useEffect(() => {
        if (!jobs) return
        if (previousJobs) {
            const newlyCompletedJobs = jobs.filter(j => (
                j.status === 'completed' && (
                    !previousJobs.find(pj => (pj.jobId === j.jobId) && pj.status === 'completed')
                )
            ))
            if (newlyCompletedJobs.length > 0) {
                refreshFiles()
            }
        }
        setPreviousJobs(jobs)
    }, [jobs, previousJobs, refreshFiles])

    useEffect(() => {
        const cancel = onPubsubMessage(message => {
            if ((message.type === 'jobStatusChanged') || (message.type === 'newPendingJob')) {
                if (message.projectId === projectId) {
                    refreshJobs()
                }
            }
        })
        return () => {cancel()}
    }, [projectId, refreshJobs])

    const deleteJobHandler = useCallback(async (jobId: string) => {
        await deleteJob(jobId, auth)
    }, [auth])

    const deleteProjectHandler = useMemo(() => (async () => {
        await deleteProject(projectId, auth)
    }), [projectId, auth])

    const setProjectNameHandler = useCallback(async (name: any) => {
        await setProjectName(projectId, name, auth)
        refreshProject()
    }, [projectId, refreshProject, auth])

    const deleteFileHandler = useCallback(async (fileName: string) => {
        if (!project) return
        await deleteFile(project.workspaceId, projectId, fileName, auth)
    }, [project, projectId, auth])

    const fileHasBeenEdited = useMemo(() => ((fileName: string) => {
        const tab = openTabs.openTabs.find(x => x.tabName === `file:${fileName}`)
        if (!tab) return false
        return tab.editedContent !== tab.content
    }), [openTabs])

    const pendingFiles = useMemo(() => {
        if (!jobs) return undefined
        if (!files) return undefined
        const fileNames = new Set(files.map(f => f.fileName))
        const pf: ProtocaasFile[] = []
        for (const job of jobs) {
            if (['pending', 'starting', 'queued', 'running', 'failed'].includes(job.status)) {
                for (const out of job.outputFiles) {
                    if (!fileNames.has(out.fileName)) {
                        pf.push({
                            projectId: job.projectId,
                            workspaceId: job.workspaceId,
                            fileId: '',
                            userId: job.userId,
                            fileName: out.fileName,
                            size: 0,
                            timestampCreated: 0,
                            content: 'pending:' + job.status,
                            metadata: {},
                            jobId: job.jobId
                        })
                        fileNames.add(out.fileName)
                    }
                }
            }
        }
        return pf
    }, [files, jobs])

    const filesIncludingPending = useMemo(() => {
        return files && pendingFiles ? [...files, ...pendingFiles] : undefined
    }, [files, pendingFiles])

    const value: ProjectPageContextType = React.useMemo(() => ({
        projectId,
        workspaceId: project?.workspaceId ?? '',
        project,
        files,
        filesIncludingPending,
        openTabs: openTabs.openTabs,
        currentTabName: openTabs.currentTabName,
        jobs,
        openTab: (tabName: string) => openTabsDispatch({type: 'openTab', tabName}),
        closeTab: (tabName: string) => openTabsDispatch({type: 'closeTab', tabName}),
        closeAllTabs: () => openTabsDispatch({type: 'closeAllTabs'}),
        setCurrentTab: (tabName: string) => openTabsDispatch({type: 'setCurrentTab', tabName}),
        setTabContent: (tabName: string, content: string | undefined) => openTabsDispatch({type: 'setTabContent', tabName, content}),
        setTabEditedContent: (tabName: string, editedContent: string) => openTabsDispatch({type: 'setTabEditedContent', tabName, editedContent}),
        refreshFiles,
        deleteProject: deleteProjectHandler,
        setProjectName: setProjectNameHandler,
        refreshJobs,
        deleteJob: deleteJobHandler,
        deleteFile: deleteFileHandler,
        fileHasBeenEdited
    }), [project, files, filesIncludingPending, projectId, refreshFiles, openTabs, deleteProjectHandler, setProjectNameHandler, refreshJobs, jobs, deleteJobHandler, deleteFileHandler, fileHasBeenEdited])

    return (
        <ProjectPageContext.Provider value={value}>
            {children}
        </ProjectPageContext.Provider>
    )
}

export const useProject = () => {
    const context = React.useContext(ProjectPageContext)
    return context
}