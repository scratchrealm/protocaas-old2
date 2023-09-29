import { FunctionComponent, useCallback, useMemo } from "react";
import { DandiUploadTask } from "./prepareDandiUploadTask";
import { useWorkspace } from "../../WorkspacePage/WorkspacePageContext";
import { ProtocaasProcessingJobDefinition, createJob } from "../../../dbInterface/dbInterface";
import { useProject } from "../ProjectPageContext";
import { useGithubAuth } from "../../../GithubAuth/useGithubAuth";
import { ProtocaasJob } from "../../../types/protocaas-types";

type DandiUploadWindowProps = {
    dandiUploadTask: DandiUploadTask
    onClose: () => void
}

const DandiUploadWindow: FunctionComponent<DandiUploadWindowProps> = ({ dandiUploadTask, onClose }) => {
    const {computeResource} = useWorkspace()
    const {projectId, workspaceId, files} = useProject()
    const processor = useMemo(() => {
        if (!computeResource) return undefined
        for (const app of computeResource.spec?.apps || []) {
            for (const p of app.processors || []) {
                if (p.name === 'dandi_upload') {
                    return p
                }
            }
        }
        return undefined
    }, [computeResource])
    const dandiApiKey = useMemo(() => {
        if (dandiUploadTask.dandiInstance === 'dandi') {
            return localStorage.getItem('dandiApiKey') || ''
        }
        else if (dandiUploadTask.dandiInstance === 'dandi-staging') {
            return localStorage.getItem('dandiStagingApiKey') || ''
        }
        else return ''
    }, [dandiUploadTask.dandiInstance])

    const {accessToken, userId} = useGithubAuth()
    const auth = useMemo(() => (accessToken ? {githubAccessToken: accessToken, userId} : {}), [accessToken, userId])

    const handleUpload = useCallback(async () => {
        if (!processor) return
        if (!files) return
        const jobDef: ProtocaasProcessingJobDefinition = {
            processorName: processor.name,
            inputFiles: dandiUploadTask.fileNames.map((fileName, ii) => ({
                name: `inputs[${ii}]`,
                fileName
            })),
            inputParameters: [
                {
                    name: 'dandiset_id',
                    value: dandiUploadTask.dandisetId
                },
                {
                    name: 'dandiset_version',
                    value: 'draft'
                },
                {
                    name: 'dandi_instance',
                    value: dandiUploadTask.dandiInstance
                },
                {
                    name: 'dandi_api_key',
                    value: dandiApiKey
                },
                {
                    name: 'names',
                    value: dandiUploadTask.names
                }
            ],
            outputFiles: []
        }
        const job = {
            workspaceId,
            projectId,
            jobDefinition: jobDef,
            processorSpec: processor,
            files,
            batchId: undefined
        }
        console.log('CREATING JOB', job)
        await createJob(job, auth)
        onClose()
    }, [processor, dandiUploadTask, workspaceId, projectId, files, auth, dandiApiKey, onClose])
    return (
        <div style={{padding: 30}}>
            <h3>DANDI Upload</h3>
            <hr />
            <div>
                <table className="table1">
                    <tbody>
                        <tr>
                            <td>Dandiset ID: </td>
                            <td>{dandiUploadTask.dandisetId}</td>
                        </tr>
                        <tr>
                            <td>Dandiset version: </td>
                            <td>draft</td>
                        </tr>
                        <tr>
                            <td>DANDI Instance: </td>
                            <td>{dandiUploadTask.dandiInstance}</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>Files: </td>
                            <td>{dandiUploadTask.names.map(name => (
                                <span key={name}><span>{name}</span><br /></span>
                            ))}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <hr />
            <div>
                {!processor && (
                    <div style={{color: 'red'}}>
                        <p>Processor not found: dandi_upload</p>
                    </div>
                )}
                {!dandiApiKey && (
                    <div style={{color: 'red'}}>
                        <p>{dandiUploadTask.dandiInstance} API key not found</p>
                    </div>
                )}
            </div>
            <div>
                <button disabled={!processor || !dandiApiKey} onClick={handleUpload}>Upload</button>
                &nbsp;&nbsp;
                <button onClick={onClose}>Cancel</button>
            </div>
        </div>
    )
}

export default DandiUploadWindow