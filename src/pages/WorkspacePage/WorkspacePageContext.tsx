import React, { FunctionComponent, PropsWithChildren, useEffect, useMemo } from 'react';
import { createProject, deleteWorkspace, fetchProjects, fetchWorkspace, getComputeResource, setWorkspaceName, setWorkspacePubliclyReadable, setWorkspaceListed, setWorkspaceComputeResourceId, setWorkspaceUsers } from '../../dbInterface/dbInterface';
import { useGithubAuth } from '../../GithubAuth/useGithubAuth';
import { setPubNubListenChannel } from '../../pubnub/pubnub';
import { useSPMain } from '../../SPMainContext';
import { ProtocaasComputeResource, ProtocaasProject, ProtocaasWorkspace } from '../../types/protocaas-types';

type Props = {
    workspaceId: string
}

type WorkspacePageContextType = {
    workspaceId: string
    workspace: ProtocaasWorkspace | undefined
    projects?: ProtocaasProject[]
    createProject: (projectName: string) => Promise<string>
    deleteWorkspace: () => Promise<void>
    setWorkspaceUsers: (users: {userId: string, role: 'admin' | 'editor' | 'viewer'}[]) => Promise<void>
    setWorkspaceName: (name: string) => Promise<void>
    setWorkspacePubliclyReadable: (publiclyReadable: boolean) => Promise<void>
    setWorkspaceListed: (listed: boolean) => Promise<void>
    setWorkspaceComputeResourceId: (computeResourceId: string) => Promise<void>
    workspaceRole: 'none' | 'admin' | 'editor' | 'viewer' | undefined
    computeResourceId: string | undefined
    computeResource: ProtocaasComputeResource | undefined
}

const WorkspacePageContext = React.createContext<WorkspacePageContextType>({
    workspaceId: '',
    workspace: undefined,
    projects: undefined,
    createProject: async () => {return ''},
    deleteWorkspace: async () => {},
    setWorkspaceUsers: async () => {},
    setWorkspaceName: async () => {},
    setWorkspacePubliclyReadable: async () => {},
    setWorkspaceListed: async () => {},
    setWorkspaceComputeResourceId: async () => {},
    workspaceRole: undefined,
    computeResourceId: undefined,
    computeResource: undefined
})

export const SetupWorkspacePage: FunctionComponent<PropsWithChildren<Props>> = ({children, workspaceId}) => {
    const [projects, setProjects] = React.useState<ProtocaasProject[] | undefined>(undefined)
    const [workspace, setWorkspace] = React.useState<ProtocaasWorkspace | undefined>(undefined)
    const [projectsRefreshCode, setProjectsRefreshCode] = React.useState(0)
    const [workspaceRefreshCode, setWorkspaceRefreshCode] = React.useState(0)

    const {refreshWorkspaces} = useSPMain()

    const {accessToken, userId} = useGithubAuth()
    const auth = useMemo(() => (accessToken ? {githubAccessToken: accessToken, userId} : {}), [accessToken, userId])

    const createProjectHandler = useMemo(() => (async (projectName: string): Promise<string> => {
        const projectId = await createProject(workspaceId, projectName, auth)
        setProjectsRefreshCode(rc => rc + 1)
        return projectId
    }), [workspaceId, auth])

    const deleteWorkspaceHandler = useMemo(() => (async () => {
        await deleteWorkspace(workspaceId, auth)
        refreshWorkspaces()
    }), [workspaceId, auth, refreshWorkspaces])

    const setWorkspaceUsersHandler = useMemo(() => (async (users: {userId: string, role: 'admin' | 'editor' | 'viewer'}[]) => {
        await setWorkspaceUsers(workspaceId, users, auth)
        setWorkspaceRefreshCode(rc => rc + 1)
    }), [workspaceId, auth])

    const setWorkspaceNameHandler = useMemo(() => (async (name: string) => {
        await setWorkspaceName(workspaceId, name, auth)
        setWorkspaceRefreshCode(rc => rc + 1)
    }), [workspaceId, auth])

    const setWorkspacePubliclyReadableHandler = useMemo(() => (async (publiclyReadable: boolean) => {
        await setWorkspacePubliclyReadable(workspaceId, publiclyReadable, auth)
        setWorkspaceRefreshCode(rc => rc + 1)
    }), [workspaceId, auth])

    const setWorkspaceListedHandler = useMemo(() => (async (listed: boolean) => {
        await setWorkspaceListed(workspaceId, listed, auth)
        setWorkspaceRefreshCode(rc => rc + 1)
    }), [workspaceId, auth])

    const setWorkspaceComputeResourceIdHandler = useMemo(() => (async (computeResourceId: string) => {
        await setWorkspaceComputeResourceId(workspaceId, computeResourceId, auth)
        setWorkspaceRefreshCode(rc => rc + 1)
    }), [workspaceId, auth])

    useEffect(() => {
        (async () => {
            setProjects(undefined)
            if (!workspaceId) return
            const projects = await fetchProjects(workspaceId, auth)
            setProjects(projects)
        })()
    }, [projectsRefreshCode, workspaceId, auth])

    useEffect(() => {
        (async () => {
            setWorkspace(undefined)
            if (!workspaceId) return
            const workspace = await fetchWorkspace(workspaceId, auth)
            setWorkspace(workspace)
        })()
    }, [workspaceId, workspaceRefreshCode, auth])

    const workspaceRole: 'admin' | 'viewer' | 'none' | 'editor' | undefined = useMemo(() => {
        if (!workspace) return undefined
        if (userId) {
            if (userId.startsWith('admin|')) return 'admin'
            if (workspace.ownerId === userId) return 'admin'
            const user = workspace.users.find(user => user.userId === userId)
            if (user) {
                return user.role
            }
        }
        return workspace.publiclyReadable ? 'viewer' : 'none'
    }, [workspace, userId])

    useEffect(() => {
        const computeResourceId = workspace?.computeResourceId || import.meta.env.VITE_DEFAULT_COMPUTE_RESOURCE_ID
        if (computeResourceId) {
            setPubNubListenChannel(computeResourceId)
        }
    }, [workspace?.computeResourceId])

    const [computeResource, setComputeResource] = React.useState<ProtocaasComputeResource | undefined>(undefined)
    useEffect(() => {
        let canceled = false
        const load = async () => {
            if (!workspace) return
            const computeResourceId = workspace.computeResourceId || import.meta.env.VITE_DEFAULT_COMPUTE_RESOURCE_ID
            if (!computeResourceId) return
            const cr = await getComputeResource(computeResourceId)
            if (canceled) return
            setComputeResource(cr)
        }
        load()
        return () => {canceled = true}
    }, [workspace])

    const value = React.useMemo(() => ({
        workspaceId,
        workspace,
        projects,
        createProject: createProjectHandler,
        deleteWorkspace: deleteWorkspaceHandler,
        setWorkspaceUsers: setWorkspaceUsersHandler,
        setWorkspaceName: setWorkspaceNameHandler,
        setWorkspacePubliclyReadable: setWorkspacePubliclyReadableHandler,
        setWorkspaceListed: setWorkspaceListedHandler,
        setWorkspaceComputeResourceId: setWorkspaceComputeResourceIdHandler,
        workspaceRole,
        computeResourceId: workspace?.computeResourceId || import.meta.env.VITE_DEFAULT_COMPUTE_RESOURCE_ID,
        computeResource
    }), [projects, workspace, createProjectHandler, deleteWorkspaceHandler, setWorkspaceUsersHandler, setWorkspaceNameHandler, setWorkspacePubliclyReadableHandler, setWorkspaceListedHandler, setWorkspaceComputeResourceIdHandler, workspaceRole, computeResource, workspaceId])

    return (
        <WorkspacePageContext.Provider value={value}>
            {children}
        </WorkspacePageContext.Provider>
    )
}

export const useWorkspace = () => {
    const context = React.useContext(WorkspacePageContext)
    return {
        workspaceId: context.workspaceId,
        workspace: context.workspace,
        projects: context.projects,
        createProject: context.createProject,
        deleteWorkspace: context.deleteWorkspace,
        setWorkspaceUsers: context.setWorkspaceUsers,
        setWorkspaceName: context.setWorkspaceName,
        setWorkspacePubliclyReadable: context.setWorkspacePubliclyReadable,
        setWorkspaceListed: context.setWorkspaceListed,
        setWorkspaceComputeResourceId: context.setWorkspaceComputeResourceId,
        workspaceRole: context.workspaceRole,
        computeResourceId: context.computeResourceId,
        computeResource: context.computeResource
    }
}