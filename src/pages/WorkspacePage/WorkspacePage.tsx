import { FunctionComponent } from "react";
import HBoxLayout from "../../components/HBoxLayout";
import useRoute from "../../useRoute";
import ComputeResourcesPage from "../ComputeResourcePage/ComputeResourcePage";
import ProcessorsView from "../ProjectPage/ProcessorsView";
import { SetupWorkspacePage, useWorkspace } from "../WorkspacePage/WorkspacePageContext";
import WorkspaceHome from "./WorkspaceHome";
import { SetupComputeResources } from "../ComputeResourcesPage/ComputeResourcesContext";

type Props = {
    width: number
    height: number
    workspaceId: string
}

const WorkspacePage: FunctionComponent<Props> = ({workspaceId, width, height}) => {
    return (
        <SetupWorkspacePage
            workspaceId={workspaceId}
        >
            <SetupComputeResources>
                <WorkspacePageChild
                    width={width}
                    height={height}
                    workspaceId={workspaceId}
                />
            </SetupComputeResources>
        </SetupWorkspacePage>
    )
}

export type WorkspacePageViewType = 'workspace-home' | 'processors' | 'compute-resource'

type WorkspacePageView = {
    type: WorkspacePageViewType
    label: string
}

const workspacePageViews: WorkspacePageView[] = [
    {
        type: 'workspace-home',
        label: 'Workspace home'
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

const WorkspacePageChild: FunctionComponent<Props> = ({width, height}) => {
    const leftMenuPanelWidth = 150
    return (
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
    )
}

type LeftMenuPanelProps = {
    width: number
    height: number
}

const LeftMenuPanel: FunctionComponent<LeftMenuPanelProps> = ({width, height}) => {
    const {route, setRoute} = useRoute()
    if (route.page !== 'workspace') throw Error(`Unexpected route ${JSON.stringify(route)}`)
    const {workspaceId} = useWorkspace()
    const currentView = route.tab || 'workapace-home'
    return (
        <div style={{position: 'absolute', width, height, overflow: 'hidden', background: '#fafafa'}}>
            {
                workspacePageViews.map(view => (
                    <div
                        key={view.type}
                        style={{padding: 10, cursor: 'pointer', background: currentView === view.type ? '#ddd' : 'white'}}
                        onClick={() => setRoute({page: 'workspace', workspaceId, tab: view.type})}
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
    const {computeResourceId} = useWorkspace()
    const {route} = useRoute()
    if (route.page !== 'workspace') throw Error(`Unexpected route ${JSON.stringify(route)}`)
    const currentView = route.tab || 'workspace-home'

    return (
        <div style={{position: 'absolute', width, height, overflow: 'hidden', background: 'white'}}>
            <div style={{position: 'absolute', width, height, visibility: currentView === 'workspace-home' ? undefined : 'hidden'}}>
                <WorkspaceHome
                    width={width}
                    height={height}
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
        </div>
    )
}

export default WorkspacePage