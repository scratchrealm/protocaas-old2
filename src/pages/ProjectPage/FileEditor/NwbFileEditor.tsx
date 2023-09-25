import { FunctionComponent, useCallback, useEffect, useMemo, useState } from "react";
import { useModalDialog } from "../../../ApplicationBar";
import Hyperlink from "../../../components/Hyperlink";
import ModalWindow from "../../../components/ModalWindow/ModalWindow";
import Splitter from "../../../components/Splitter";
import { fetchFile } from "../../../dbInterface/dbInterface";
import { useGithubAuth } from "../../../GithubAuth/useGithubAuth";
import { getRemoteH5File, RemoteH5File } from "../../../RemoteH5File/RemoteH5File";
import { ComputeResourceSpecProcessor, ProtocaasFile } from "../../../types/protocaas-types";
import { useWorkspace } from "../../WorkspacePage/WorkspacePageContext";
import { AssetResponse } from "../DandiNwbSelector/types";
import JobsWindow from "../JobsWindow/JobsWindow";
import LoadNwbInPythonWindow from "../LoadNwbInPythonWindow/LoadNwbInPythonWindow";
import { useProject } from "../ProjectPageContext";
import RunSpikeSortingWindow from "./RunSpikeSortingWindow/RunSpikeSortingWindow";
import SpikeSortingOutputSection from "./SpikeSortingOutputSection/SpikeSortingOutputSection";


type Props = {
    fileName: string
    width: number
    height: number
}

const NwbFileEditor: FunctionComponent<Props> = ({fileName, width, height}) => {
    return (
        <Splitter
            width={width}
            height={height}
            initialPosition={height * 2 / 3}
            direction="vertical"
        >
            <NwbFileEditorChild
                width={0}
                height={0}
                fileName={fileName}
            />
            <JobsWindow
                width={0}
                height={0}
                fileName={fileName}
            />
        </Splitter>
    )
}

export const useNwbFile = (nwbUrl: string) => {
    const [nwbFile, setNwbFile] = useState<RemoteH5File | undefined>(undefined)
    useEffect(() => {
        let canceled = false
        if (!nwbUrl) return
        ; (async () => {
            const f = await getRemoteH5File(nwbUrl, undefined)
            if (canceled) return
            setNwbFile(f)
        })()
        return () => {canceled = true}
    }, [nwbUrl])
    return nwbFile
}

export const useElectricalSeriesPaths = (nwbFile: RemoteH5File | undefined) => {
    const [electricalSeriesPaths, setElectricalSeriesPaths] = useState<string[] | undefined>(undefined)
    useEffect(() => {
        let canceled = false
        setElectricalSeriesPaths(undefined)
        ; (async () => {
            if (!nwbFile) return
            const grp = await nwbFile.getGroup('acquisition')
            if (canceled) return
            if (!grp) return
            const pp: string[] = []
            for (const sg of grp.subgroups) {
                if (sg.attrs['neurodata_type'] === 'ElectricalSeries') {
                    pp.push(sg.path)
                }
            }
            setElectricalSeriesPaths(pp)
        })()
        return () => {canceled = true}
    }, [nwbFile])
    return electricalSeriesPaths
}

const NwbFileEditorChild: FunctionComponent<Props> = ({fileName, width, height}) => {
    const [assetResponse, setAssetResponse] = useState<AssetResponse | null>(null)

    const {projectId, project, jobs} = useProject()

    const {accessToken, userId} = useGithubAuth()
    const auth = useMemo(() => (accessToken ? {githubAccessToken: accessToken, userId} : {}), [accessToken, userId])

    const [nbFile, setProtocaasFile] = useState<ProtocaasFile | undefined>(undefined)
    useEffect(() => {
        let canceled = false
        ; (async () => {
            const f = await fetchFile(projectId, fileName, auth)
            if (canceled) return
            setProtocaasFile(f)
        })()
        return () => {canceled = true}
    }, [projectId, fileName, auth])

    const metadata = nbFile?.metadata
    const cc = nbFile?.content || ''
    const nwbUrl = cc.startsWith('url:') ? cc.slice('url:'.length) : ''
    const nwbFile = useNwbFile(nwbUrl)
    const electricalSeriesPaths = useElectricalSeriesPaths(nwbFile)

    const dandisetId = metadata?.dandisetId || ''
    const dandisetVersion = metadata?.dandisetVersion || ''
    const dandiAssetId = metadata?.dandiAssetId || ''
    const dandiAssetPath = metadata?.dandiAssetPath || ''
    const dandiStaging = metadata?.dandiStaging || false

    const stagingStr = dandiStaging ? '-staging' : ''
    const stagingStr2 = dandiStaging ? 'gui-staging.' : ''

    const handleOpenInNeurosift = useCallback(() => {
        const u = `https://flatironinstitute.github.io/neurosift/?p=/nwb&url=${nwbUrl}`
        window.open(u, '_blank')
    }, [nwbUrl])

    useEffect(() => {
        if (!dandisetId) return
        if (!dandiAssetId) return
        ; (async () => {
            const response = await fetch(`https://api${stagingStr}.dandiarchive.org/api/dandisets/${dandisetId}/versions/${dandisetVersion}/assets/${dandiAssetId}/`)
            if (response.status === 200) {
                const json = await response.json()
                const assetResponse: AssetResponse = json
                setAssetResponse(assetResponse)
            }
        })()
    }, [dandisetId, dandiAssetId, dandisetVersion, stagingStr])

    if ((assetResponse) && (dandiAssetPath !== assetResponse.path)) {
        console.warn(`Mismatch between dandiAssetPath (${dandiAssetPath}) and assetResponse.path (${assetResponse.path})`)
    }

    const {visible: runSpikeSortingWindowVisible, handleOpen: openRunSpikeSortingWindow, handleClose: closeRunSpikeSortingWindow} = useModalDialog()
    const [selectedSpikeSortingProcessor, setSelectedSpikeSortingProcessor] = useState<string | undefined>(undefined)

    const {visible: loadNwbInPythonWindowVisible, handleOpen: openLoadNwbInPythonWindow, handleClose: closeLoadNwbInPythonWindow} = useModalDialog()

    const spikeSortingJob = useMemo(() => {
        if (!jobs) return undefined
        if (!nbFile) return undefined
        if (!nbFile.jobId) return undefined
        const job = jobs.find(j => (j.jobId === nbFile.jobId))
        if (!job) return
        if (job.processorSpec.tags.map(t => t.tag).includes('spike_sorter')) {
            return job
        }
        return undefined
    }, [jobs, nbFile])

    return (
        <div style={{position: 'absolute', width, height, background: 'white'}}>
            <hr />
            <table className="table1">
                <tbody>
                    <tr>
                        <td>URL:</td>
                        <td>{nwbUrl}</td>
                    </tr>
                    <tr>
                        <td>Dandiset:</td>
                        <td>
                            {dandisetId && <a href={`https://${stagingStr2}dandiarchive.org/dandiset/${dandisetId}/${dandisetVersion}`} target="_blank" rel="noreferrer">
                                {dandisetId} ({dandisetVersion || ''})
                            </a>}
                        </td>
                    </tr>
                    <tr>
                        <td>DANDI Path:</td>
                        <td>
                            {assetResponse?.path || ''}
                        </td>
                    </tr>
                    <tr>

                    </tr>
                </tbody>
            </table>
            <div>&nbsp;</div>
            <ul>
            {
                nwbUrl && (
                    <li>
                        <Hyperlink onClick={handleOpenInNeurosift}>Open NWB file in Neurosift</Hyperlink>
                    </li>
                )
            }
            {
                nwbUrl && (
                    <li>
                        <Hyperlink onClick={openLoadNwbInPythonWindow}>Load NWB file in Python</Hyperlink>
                    </li>
                )
            }
            </ul>
            {
                spikeSortingJob && (
                    <SpikeSortingOutputSection
                        fileName={fileName}
                        spikeSortingJob={spikeSortingJob}
                    />
                )
            }
            <div>&nbsp;</div>
            {
                electricalSeriesPaths && (
                    electricalSeriesPaths.length > 0 ? (
                        <RunSpikeSortingComponent
                            onSelect={(processorName) => {setSelectedSpikeSortingProcessor(processorName); openRunSpikeSortingWindow();}}
                        />
                    ) : (
                        <div>No electrical series found</div>
                    )       
                )
            }
            <hr />
            <ModalWindow
                open={runSpikeSortingWindowVisible}
                onClose={closeRunSpikeSortingWindow}
            >
                <RunSpikeSortingWindow
                    onClose={closeRunSpikeSortingWindow}
                    fileName={fileName}
                    spikeSortingProcessorName={selectedSpikeSortingProcessor}
                    nwbFile={nwbFile}
                />
            </ModalWindow>
            <ModalWindow
                open={loadNwbInPythonWindowVisible}
                onClose={closeLoadNwbInPythonWindow}
            >
                {project && <LoadNwbInPythonWindow
                    onClose={closeLoadNwbInPythonWindow}
                    project={project}
                    fileName={fileName}
                />}
            </ModalWindow>
        </div>
    )
}

type RunSpikeSortingComponentProps = {
    onSelect?: (processorName: string) => void
}

const RunSpikeSortingComponent: FunctionComponent<RunSpikeSortingComponentProps> = ({onSelect}) => {
    const {computeResource} = useWorkspace()
    const spikeSorterProcessors = useMemo(() => {
        const ret: ComputeResourceSpecProcessor[] = []
        for (const app of computeResource?.spec?.apps || []) {
            for (const p of app.processors || []) {
                if (p.tags.map(t => t.tag).includes('spike_sorter')) {
                    ret.push(p)
                }
            }
        }
        return ret
    }, [computeResource])
    if (!computeResource) return <div>Loading compute resource spec...</div>
    if (spikeSorterProcessors.length === 0) return <div>No spike sorter processors found</div>
    return (
        <div>
            Run spike sorting using:
            <ul>
                {
                    spikeSorterProcessors.map((processor, i) => (
                        <li key={i}>
                            <Hyperlink onClick={() => {onSelect && onSelect(processor.name)}}>
                                {processor.name}
                            </Hyperlink>
                        </li>
                    ))
                }
            </ul>
        </div>
    )
}

export default NwbFileEditor