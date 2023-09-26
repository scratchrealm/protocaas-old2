import { FunctionComponent, useCallback, useEffect, useMemo, useReducer, useState } from "react"
import Hyperlink from "../../../components/Hyperlink"
import { defaultJobDefinition, fetchFile, protocaasJobDefinitionReducer, ProtocaasProcessingJobDefinition } from "../../../dbInterface/dbInterface"
import { useGithubAuth } from "../../../GithubAuth/useGithubAuth"
import { ComputeResourceSpecProcessor, ProtocaasFile } from "../../../types/protocaas-types"
import { useWorkspace } from "../../WorkspacePage/WorkspacePageContext"
import { useNwbFile } from "../FileEditor/NwbFileEditor"
import EditJobDefinitionWindow from "../FileEditor/RunSpikeSortingWindow/EditJobDefinitionWindow"
import { useProject } from "../ProjectPageContext"
import { createJob } from "../../../dbInterface/dbInterface"

type Props = {
    filePaths: string[]
    onClose: () => void
}

const RunBatchSpikeSortingWindow: FunctionComponent<Props> = ({ filePaths, onClose }) => {
    const {projectId, workspaceId, files} = useProject()
    const {accessToken, userId} = useGithubAuth()
    const auth = useMemo(() => (accessToken ? {githubAccessToken: accessToken, userId} : {}), [accessToken, userId])

    const [operating, setOperating] = useState(false)
    const [operatingMessage, setOperatingMessage] = useState<string | undefined>(undefined)

    const [selectedSpikeSortingProcessor, setSelectedSpikeSortingProcessor] = useState<string | undefined>(undefined)

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

    const processor = useMemo(() => {
        if (!selectedSpikeSortingProcessor) return undefined
        return spikeSorterProcessors.find(p => (p.name === selectedSpikeSortingProcessor))
    }, [spikeSorterProcessors, selectedSpikeSortingProcessor])

    const [jobDefinition, jobDefinitionDispatch] = useReducer(protocaasJobDefinitionReducer, defaultJobDefinition)
    useEffect(() => {
        if (!processor) return
        const jd: ProtocaasProcessingJobDefinition = {
            inputFiles: [
                {
                    name: 'input',
                    fileName: '*'
                }
            ],
            outputFiles: [
                {
                    name: 'output',
                    fileName: `*`
                }
            ],
            inputParameters: processor.parameters.map(p => ({
                name: p.name,
                value: p.default
            })),
            processorName: processor.name
        }
        jobDefinitionDispatch({
            type: 'setJobDefinition',
            jobDefinition: jd
        })
    }, [processor])

    const [pcFile, setProtocaasFile] = useState<ProtocaasFile | undefined>(undefined)
    useEffect(() => {
        let canceled = false
        if (filePaths.length === 0) return
        ; (async () => {
            const f = await fetchFile(projectId, filePaths[0], auth)
            if (canceled) return
            setProtocaasFile(f)
        })()
        return () => {canceled = true}
    }, [filePaths, projectId, auth])

    const cc = pcFile?.content || ''
    const nwbUrl = cc.startsWith('url:') ? cc.slice('url:'.length) : ''
    const nwbFile = useNwbFile(nwbUrl)

    const [valid, setValid] = useState(false)

    const [overwriteExistingOutputs, setOverwriteExistingOutputs] = useState(false)
    const [outputPrefix, setOutputPrefix] = useState('')
    useEffect(() => {
        if (!processor) return
        setOutputPrefix(`.${processor.name}`)
    }, [processor])

    const handleSubmit = useCallback(async () => {
        if (!processor) return
        if (!files) return
        setOperating(true)
        setOperatingMessage('Preparing...')
        const batchId = createRandomId(8)
        for (let i = 0; i < filePaths.length; i++) {
            const filePath = filePaths[i]
            const jobDefinition2: ProtocaasProcessingJobDefinition = deepCopy(jobDefinition)
            const outputFileName = `${outputPrefix}/${filePath}`
            const outputExists = files.find(f => (f.fileName === outputFileName))
            if (outputExists && !overwriteExistingOutputs) {
                continue
            }
            setOperatingMessage(`Submitting job ${filePath} (${i + 1} of ${filePaths.length})`)
            jobDefinition2.inputFiles[0].fileName = filePath
            jobDefinition2.outputFiles[0].fileName = outputFileName
            await createJob({
                workspaceId,
                projectId,
                jobDefinition: jobDefinition2,
                processorSpec: processor,
                batchId
            }, auth)
        }
        setOperatingMessage(undefined)
        setOperating(false)
        onClose()
    }, [workspaceId, projectId, jobDefinition, processor, filePaths, files, overwriteExistingOutputs, outputPrefix, auth, onClose])

    if (!selectedSpikeSortingProcessor) {
        return (
            <SelectProcessor
                processors={spikeSorterProcessors}
                onSelected={setSelectedSpikeSortingProcessor}
            />
        )
    }
    return (
        <div>
            <h3>Batch spike sorting of {filePaths.length} files using {selectedSpikeSortingProcessor}</h3>
            <div>
                <table className="table1" style={{maxWidth: 500}}>
                    <tbody>
                        <tr>
                            <td>Overwrite existing outputs</td>
                            <td>
                                <input type="checkbox" checked={overwriteExistingOutputs} onChange={evt => setOverwriteExistingOutputs(evt.target.checked)} />
                            </td>
                        </tr>
                        <tr>
                            <td>Output prefix</td>
                            <td>
                                <input type="text" value={outputPrefix} onChange={evt => setOutputPrefix(evt.target.value)} /> {`/*`}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div>&nbsp;</div>
            <div>
                <button disabled={!valid || operating} onClick={handleSubmit}>Submit</button>
                &nbsp;
                {
                    operatingMessage && (
                        <span>{operatingMessage}</span>
                    )
                }
            </div>
            {
                !valid ? (
                    <div>
                        <span style={{color: 'red'}}>There are errors in the job definition.</span>
                    </div>
                ) : <div>&nbsp;</div>
            }
            {processor && (
                <EditJobDefinitionWindow
                    jobDefinition={jobDefinition}
                    jobDefinitionDispatch={jobDefinitionDispatch}
                    processor={processor}
                    nwbFile={nwbFile}
                    setValid={setValid}
                    readOnly={operating}
                />
            )}
        </div>
    )
}

type SelectProcessorProps = {
    processors: ComputeResourceSpecProcessor[]
    onSelected: (processorName: string) => void
}

const SelectProcessor: FunctionComponent<SelectProcessorProps> = ({processors, onSelected}) => {
    return (
        <div>
            <h3>Select a spike sorter</h3>
            <ul>
                {
                    processors.map((processor, i) => (
                        <li key={i}>
                            <Hyperlink onClick={() => {onSelected(processor.name)}}>
                                {processor.name}
                            </Hyperlink>
                        </li>
                    ))
                }
            </ul>
        </div>
    )
}

const deepCopy = (x: any) => {
    return JSON.parse(JSON.stringify(x))
}

const createRandomId = (numChars: number) => {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    let ret = ''
    for (let i = 0; i < numChars; i++) {
        const j = Math.floor(Math.random() * chars.length)
        ret += chars[j]
    }
    return ret
}

export default RunBatchSpikeSortingWindow