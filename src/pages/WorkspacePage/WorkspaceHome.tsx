import { Settings } from "@mui/icons-material";
import { FunctionComponent } from "react";
import { useModalDialog } from "../../ApplicationBar";
import ModalWindow from "../../components/ModalWindow/ModalWindow";
import SmallIconButton from "../../components/SmallIconButton";
import { timeAgoString } from "../../timeStrings";
import { useWorkspace } from "../WorkspacePage/WorkspacePageContext";
import ProjectsMenuBar from "./ProjectsMenuBar";
import ProjectsTable from "./ProjectsTable";
import WorkspaceSettingsWindow from "./WorkspaceSettingsWindow";
import ComputeResourceNameDisplay from "../../ComputeResourceNameDisplay";

type Props = {
    width: number
    height: number
}

const WorkspaceHome: FunctionComponent<Props> = ({width, height}) => {
    const {workspace} = useWorkspace()
    const {visible: settingsWindowVisible, handleOpen: openSettingsWindow, handleClose: closeSettingsWindow} = useModalDialog()
    return (
        <div style={{position: 'absolute', width, height, overflowY: 'auto', padding: 10, background: 'white'}}>
            <div style={{fontSize: 20, fontWeight: 'bold'}}>Workspace: {workspace?.name}</div>
            &nbsp;
            <table className="table1" style={{maxWidth: 500}}>
                <tbody>
                    <tr>
                        <td>Workspace name:</td>
                        <td>{workspace?.name}</td>
                    </tr>
                    <tr>
                        <td>Workspace ID:</td>
                        <td>{workspace?.workspaceId}</td>
                    </tr>
                    <tr>
                        <td>Compute resource:</td>
                        <td>{workspace ? <ComputeResourceNameDisplay computeResourceId={workspace.computeResourceId} link={true} /> : ''}</td>
                    </tr>
                    <tr>
                        <td>Created:</td>
                        <td>{timeAgoString(workspace?.timestampCreated)}</td>
                    </tr>
                    <tr>
                        <td>Modified:</td>
                        <td>{timeAgoString(workspace?.timestampModified)}</td>
                    </tr>
                </tbody>
            </table>
            <div style={{paddingTop: 10}}>
                <button onClick={openSettingsWindow} title="Workspace settings"><SmallIconButton icon={<Settings />} /> Settings</button>
            </div>
            <hr />
            <div style={{padding: 10}}>
                <ProjectsMenuBar />
                <div style={{ height: 10 }} />
                <ProjectsTable />
            </div>
            <ModalWindow
                open={settingsWindowVisible}
                onClose={closeSettingsWindow}
            >
                <WorkspaceSettingsWindow />
            </ModalWindow>
        </div>
    )
}

export default WorkspaceHome