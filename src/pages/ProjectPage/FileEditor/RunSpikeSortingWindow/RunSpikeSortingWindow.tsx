import { FunctionComponent, useCallback, useEffect, useMemo, useReducer, useState } from "react"
import { createJob, defaultJobDefinition, protocaasJobDefinitionReducer, ProtocaasProcessingJobDefinition } from "../../../../dbInterface/dbInterface"
import { useGithubAuth } from "../../../../GithubAuth/useGithubAuth"
import { RemoteH5File } from "../../../../RemoteH5File/RemoteH5File"
import { useWorkspace } from "../../../WorkspacePage/WorkspacePageContext"
import { useProject } from "../../ProjectPageContext"
import EditJobDefinitionWindow from "./EditJobDefinitionWindow"

type RunSpikeSortingWindowProps = {
    fileName: string
    onClose: () => void
    spikeSortingProcessorName?: string
    nwbFile?: RemoteH5File
}

const RunSpikeSortingWindow: FunctionComponent<RunSpikeSortingWindowProps> = ({fileName, onClose, spikeSortingProcessorName, nwbFile}) => {
    const {projectId, workspaceId} = useProject()
    const {computeResource} = useWorkspace()

    const allProcessors = useMemo(() => {
        if (!computeResource) return []
        if (!computeResource.spec) return []
        return computeResource.spec.apps.map(app => (app.processors || [])).flat()
    }, [computeResource])

    const processor = useMemo(() => {
        return allProcessors.find(p => (p.name === spikeSortingProcessorName))
    }, [allProcessors, spikeSortingProcessorName])

    const [submitting, setSubmitting] = useState<boolean>(false)

    const {accessToken, userId} = useGithubAuth()
    const auth = useMemo(() => (accessToken ? {githubAccessToken: accessToken, userId} : {}), [accessToken, userId])

    const [jobDefinition, jobDefinitionDispatch] = useReducer(protocaasJobDefinitionReducer, defaultJobDefinition)
    useEffect(() => {
        if (!processor) return
        const jd: ProtocaasProcessingJobDefinition = {
            inputFiles: [
                {
                    name: 'input',
                    fileName
                }
            ],
            outputFiles: [
                {
                    name: 'output',
                    fileName: `.job-outputs/${processor.name}/$\{job-id}/output.nwb`
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
    }, [processor, fileName])

    const handleSubmit = useCallback(async () => {
        if (!spikeSortingProcessorName) return
        if (!jobDefinition) return
        if (!processor) return
        setSubmitting(true)
        try {
            await createJob({workspaceId, projectId, jobDefinition, processorSpec: processor}, auth)
            onClose()
        }
        finally {
            setSubmitting(false)
        }
    }, [workspaceId, projectId, jobDefinition, auth, spikeSortingProcessorName, onClose, processor])

    const [valid, setValid] = useState<boolean>(false)
    const submitEnabled = !submitting && valid && !!processor

    useEffect(() => {
        // do this so that we can identify in the dev console problems that would cause infinite recursion
        console.info('Job definition:', jobDefinition)
    }, [jobDefinition])

    return (
        <div>
            <h3>Run spike sorting</h3>
            <div>
                Spike sorter: {processor?.name}
            </div>
            <div>&nbsp;</div>
            <div>
                <button onClick={handleSubmit} disabled={!submitEnabled}>Submit job</button>
            </div>
            <hr />
            {
                processor && <EditJobDefinitionWindow
                    jobDefinition={jobDefinition}
                    jobDefinitionDispatch={jobDefinitionDispatch}
                    processor={processor}
                    nwbFile={nwbFile}
                    setValid={setValid}
                />
            }
            <hr />
        </div>
    )
}

export default RunSpikeSortingWindow