import { FunctionComponent, useCallback, useEffect, useMemo, useState } from "react"
import { useGithubAuth } from "../../GithubAuth/useGithubAuth"
import { useSPMain } from "../../SPMainContext"

type Props = {
    dandisetId: string
}

const ImportDandisetPage: FunctionComponent<Props> = ({dandisetId}) => {
    const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string | '<create-new>'>('<create-new>')
    const [projectName, setProjectName] = useState<string>('')
    useEffect(() => {
        setProjectName(`DANDI dandisetId`)
    }, [dandisetId])
    const submitEnabled = useMemo(() => {
        if (!projectName) return false
        return true
    }, [projectName])
    const {createWorkspace} = useSPMain()
    const handleCreateProject = useCallback(async () => {
        // TODO
    }, [])
    return (
        <div style={{padding: 20}}>
            <h3>Import dandiset {dandisetId}</h3>
            <div>&nbsp;</div>
            <ProjectNameInputComponent
                projectName={projectName}
                onProjectNameChanged={setProjectName}
            />
            <div>&nbsp;</div>
            <WorkspaceSelectionComponent
                selectedWorkspaceId={selectedWorkspaceId}
                onSelectedWorkspaceIdChanged={setSelectedWorkspaceId}
            />
            <div>&nbsp;</div>
            <button
                disabled={!submitEnabled}
                onClick={handleCreateProject}
            >
                Create new project and import dandiset
            </button>
        </div>
    )
}

type ProjectNameInputComponentProps = {
    projectName: string
    onProjectNameChanged: (projectName: string) => void
}

const ProjectNameInputComponent: FunctionComponent<ProjectNameInputComponentProps> = ({projectName, onProjectNameChanged}) => {
    return (
        <div>
            <label>Project name:</label>
            <input
                type="text"
                value={projectName}
                onChange={(e) => onProjectNameChanged(e.target.value)}
            />
        </div>
    )
}

type WorkspaceSelectionComponentProps = {
    selectedWorkspaceId: string | '<create-new>'
    onSelectedWorkspaceIdChanged: (workspaceId: string | '<create-new>') => void
}

const WorkspaceSelectionComponent: FunctionComponent<WorkspaceSelectionComponentProps> = ({selectedWorkspaceId, onSelectedWorkspaceIdChanged}) => {
    // Give the user a choice of whether to create a new project or
    // use an existing one. If using existing, have a dropdown selection for the existing workspace
    const {workspaces} = useSPMain()
    const {userId} = useGithubAuth()

    const userWorkspaces = useMemo(() => {
        if (!workspaces) return []
        return workspaces.filter(w => {
            if (w.ownerId === userId) return true
            if (w.users.find(u => ((u.role === 'admin' || u.role === 'editor') && u.userId === userId))) return true
            return false
        })
    }, [workspaces, userId])

    return (
        <div>
            <label>Workspace:</label>
            <select
                value={selectedWorkspaceId}
                onChange={(e) => onSelectedWorkspaceIdChanged(e.target.value as string)}
            >
                <option value="<create-new>">Create new workspace</option>
                {
                    userWorkspaces.map(w => (
                        <option key={w.workspaceId} value={w.workspaceId}>{w.name}</option>
                    ))
                }
            </select>
        </div>
    )
}

export default ImportDandisetPage