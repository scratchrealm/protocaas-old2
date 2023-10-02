import { FunctionComponent, useCallback, useMemo, useState } from "react";
import { useModalDialog } from "../../ApplicationBar";
import HBoxLayout from "../../components/HBoxLayout";
import ModalWindow from "../../components/ModalWindow/ModalWindow";
import { setUrlFile } from "../../dbInterface/dbInterface";
import { useGithubAuth } from "../../GithubAuth/useGithubAuth";
import useRoute from "../../useRoute";
import ComputeResourcesPage from "../ComputeResourcePage/ComputeResourcePage";
import { SetupWorkspacePage, useWorkspace } from "../WorkspacePage/WorkspacePageContext";
import DandiNwbSelector from "./DandiImport/DandiNwbSelector";
import ManualNwbSelector from "./ManualNwbSelector/ManualNwbSelector";
import ProcessorsView from "./ProcessorsView";
import ProjectFiles from "./ProjectFiles";
import ProjectHome from "./ProjectHome";
import ProjectJobs from "./ProjectJobs";
import { SetupProjectPage, useProject } from "./ProjectPageContext";
import RunBatchSpikeSortingWindow from "./RunBatchSpikeSortingWindow/RunBatchSpikeSortingWindow";
import { SetupComputeResources } from "../ComputeResourcesPage/ComputeResourcesContext";
import { DandiUploadTask } from "./DandiUpload/prepareDandiUploadTask";
import DandiUploadWindow from "./DandiUpload/DandiUploadWindow";

type Props = {
    width: number
    height: number
    projectId: string
}

const ProjectPage: FunctionComponent<Props> = ({projectId, width, height}) => {
    return (
        <SetupProjectPage
            projectId={projectId}
        >
            <ProjectPageChild
                width={width}
                height={height}
                projectId={projectId}
            />
        </SetupProjectPage>
    )
}

export type ProjectPageViewType = 'project-home' | 'project-files' | 'project-jobs' | 'dandi-import' | 'manual-import' | 'processors' | 'compute-resource'

type ProjectPageView = {
    type: ProjectPageViewType
    label: string
}

const projectPageViews: ProjectPageView[] = [
    {
        type: 'project-home',
        label: 'Project home'
    },
    {
        type: 'project-files',
        label: 'Files'
    },
    {
        type: 'project-jobs',
        label: 'Jobs'
    },
    {
        type: 'dandi-import',
        label: 'DANDI import'
    },
    {
        type: 'manual-import',
        label: 'Manual import'
    },
    {
        type: 'processors',
        label: 'Processors'
    },
    {
        type: 'compute-resource',
        label: 'Compute resource'
    }
]

const ProjectPageChild: FunctionComponent<Props> = ({width, height}) => {
    const {workspaceId} = useProject()

    const leftMenuPanelWidth = 150
    return (
        <SetupWorkspacePage
            workspaceId={workspaceId}
        >
            <SetupComputeResources>
                <div style={{position: 'absolute', width, height, overflow: 'hidden'}}>
                    <HBoxLayout
                        widths={[leftMenuPanelWidth, width - leftMenuPanelWidth]}
                        height={height}
                    >
                        <LeftMenuPanel
                            width={0}
                            height={0}
                        />
                        <MainPanel
                            width={0}
                            height={0}
                        />
                    </HBoxLayout>
                </div>
            </SetupComputeResources>
        </SetupWorkspacePage>
    )
}

type LeftMenuPanelProps = {
    width: number
    height: number
}

const LeftMenuPanel: FunctionComponent<LeftMenuPanelProps> = ({width, height}) => {
    const {route, setRoute} = useRoute()
    const {projectId} = useProject()
    if (route.page !== 'project') throw Error(`Unexpected route ${JSON.stringify(route)}`)
    const currentView = route.tab || 'project-home'
    return (
        <div style={{position: 'absolute', width, height, overflow: 'hidden', background: '#fafafa'}}>
            {
                projectPageViews.map(view => (
                    <div
                        key={view.type}
                        style={{padding: 10, cursor: 'pointer', background: currentView === view.type ? '#ddd' : 'white'}}
                        onClick={() => setRoute({page: 'project', projectId, tab: view.type})}
                    >
                        {view.label}
                    </div>
                ))
            }
        </div>
    )
}

type MainPanelProps = {
    width: number
    height: number
}

const MainPanel: FunctionComponent<MainPanelProps> = ({width, height}) => {
    const {openTab, project, refreshFiles} = useProject()
    const {computeResourceId} = useWorkspace()
    const {accessToken, userId} = useGithubAuth()
    const auth = useMemo(() => (accessToken ? {githubAccessToken: accessToken, userId} : {}), [accessToken, userId])
    const {route, setRoute} = useRoute()
    if (route.page !== 'project') throw Error(`Unexpected route ${JSON.stringify(route)}`)
    const currentView = route.tab || 'project-home'

    const handleCreateFiles = useCallback(async (files: {fileName: string, url: string, metadata: any}[]) => {
        if (!project) {
            console.warn('No project')
            return
        }
        for (const file of files) {
            await setUrlFile(project.projectId, file.fileName, file.url, file.metadata, auth)
        }
        refreshFiles()
        if (files.length === 1) {
            openTab(`file:${files[0].fileName}`)
        }
        setRoute({page: 'project', projectId: project.projectId, tab: 'project-files'})
    }, [project, openTab, auth, refreshFiles, setRoute])

    const handleImportDandiNwbFiles = useCallback(async (files: {nwbUrl: string, dandisetId: string, dandisetVersion: string, assetId: string, assetPath: string, useStaging: boolean}[]) => {
        const files2: {
            fileName: string
            url: string
            metadata: {
                dandisetId: string
                dandisetVersion: string
                dandiAssetId: string
                dandiAssetPath: string
                dandiStaging: boolean
            }
        }[] = []
        for (const file of files) {
            const stagingStr = file.useStaging ? 'staging-' : ''
            const fileName = 'imported/' + stagingStr + file.dandisetId + '/' + file.assetPath
            const metadata = {
                dandisetId: file.dandisetId,
                dandisetVersion: file.dandisetVersion,
                dandiAssetId: file.assetId,
                dandiAssetPath: file.assetPath,
                dandiStaging: file.useStaging
            }
            files2.push({fileName, url: file.nwbUrl, metadata})
        }
        await handleCreateFiles(files2)
    }, [handleCreateFiles])

    const handleImportManualNwbFile = useCallback((nwbUrl: string, fileName: string) => {
        const metadata = {}
        handleCreateFiles([{fileName, url: nwbUrl, metadata}])
    }, [handleCreateFiles])

    const {visible: runSpikeSortingWindowVisible, handleOpen: openRunSpikeSortingWindow, handleClose: closeRunSpikeSortingWindow} = useModalDialog()
    const [spikeSortingFilePaths, setSpikeSortingFilePaths] = useState<string[]>([])
    const handleRunSpikeSorting = useCallback((filePaths: string[]) => {
        setSpikeSortingFilePaths(filePaths)
        openRunSpikeSortingWindow()
    }, [openRunSpikeSortingWindow])

    const {visible: dandiUploadWindowVisible, handleOpen: openDandiUploadWindow, handleClose: closeDandiUploadWindow} = useModalDialog()
    const [dandiUploadTask, setDandiUploadTask] = useState<DandiUploadTask | undefined>(undefined)
    const handleDandiUpload = useCallback((dandiUploadTask: DandiUploadTask) => {
        setDandiUploadTask(dandiUploadTask)
        openDandiUploadWindow()
    }, [openDandiUploadWindow])

    return (
        <div style={{position: 'absolute', width, height, overflow: 'hidden', background: 'white'}}>
            <div style={{position: 'absolute', width, height, visibility: currentView === 'project-home' ? undefined : 'hidden'}}>
                <ProjectHome
                    width={width}
                    height={height}
                />
            </div>
            <div style={{position: 'absolute', width, height, visibility: currentView === 'project-files' ? undefined : 'hidden'}}>
                <ProjectFiles
                    width={width}
                    height={height}
                    onRunBatchSpikeSorting={handleRunSpikeSorting}
                    onDandiUpload={handleDandiUpload}
                />
            </div>
            <div style={{position: 'absolute', width, height, visibility: currentView === 'project-jobs' ? undefined : 'hidden'}}>
                <ProjectJobs
                    width={width}
                    height={height}
                />
            </div>
            <div style={{position: 'absolute', width, height, visibility: currentView === 'dandi-import' ? undefined : 'hidden'}}>
                <DandiNwbSelector
                    width={width}
                    height={height}
                    onNwbFilesSelected={handleImportDandiNwbFiles}
                />
            </div>
            <div style={{position: 'absolute', width, height, visibility: currentView === 'manual-import' ? undefined : 'hidden'}}>
                <ManualNwbSelector
                    width={width}
                    height={height}
                    onNwbFileSelected={handleImportManualNwbFile}
                />
            </div>
            <div style={{position: 'absolute', width, height, visibility: currentView === 'processors' ? undefined : 'hidden'}}>
                <ProcessorsView
                    width={width}
                    height={height}
                />
            </div>
            <div style={{position: 'absolute', width, height, visibility: currentView === 'compute-resource' ? undefined : 'hidden'}}>
                {
                    computeResourceId && (
                        <ComputeResourcesPage
                            width={width}
                            height={height}
                            computeResourceId={computeResourceId}
                        />
                    )
                }
            </div>
            <ModalWindow
                open={runSpikeSortingWindowVisible}
                onClose={closeRunSpikeSortingWindow}
            >
                <RunBatchSpikeSortingWindow
                    filePaths={spikeSortingFilePaths}
                    onClose={closeRunSpikeSortingWindow}
                />
            </ModalWindow>
            <ModalWindow
                open={dandiUploadWindowVisible}
                onClose={closeDandiUploadWindow}
            >
                {
                    dandiUploadTask && (
                        <DandiUploadWindow
                            dandiUploadTask={dandiUploadTask}
                            onClose={closeDandiUploadWindow}
                        />
                    )
                }
            </ModalWindow>
        </div>
    )
}

export default ProjectPage