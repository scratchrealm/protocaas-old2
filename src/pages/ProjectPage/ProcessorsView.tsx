import { Build } from "@mui/icons-material"
import { FunctionComponent, useMemo } from "react"
import { ComputeResourceSpecProcessor } from "../../types/protocaas-types"
import { useWorkspace } from "../WorkspacePage/WorkspacePageContext"
import './Processor.css'

type ProcessorsViewProps = {
    width: number
    height: number
}

const ProcessorsView: FunctionComponent<ProcessorsViewProps> = ({width, height}) => {
    const {computeResource} = useWorkspace()
    const allProcessors = useMemo(() => {
        if (!computeResource) return []
        if (!computeResource.spec) return []
        return computeResource.spec.apps.map(app => (app.processors || [])).flat()
    }, [computeResource])
    if (!computeResource) return <div>Loading compute resource spec...</div>
    return (
        <div style={{position: 'absolute', width, height, overflowY: 'auto'}}>
            <hr />
            {
                allProcessors.map((processor, i) => (
                    <span key={i}>
                        <ProcessorView
                            processor={processor}
                            width={width}
                        />
                        <hr />
                    </span>
                ))
            }
        </div>
    )
}

type ProcessorViewProps = {
    processor: ComputeResourceSpecProcessor
    width: number
}

const ProcessorView: FunctionComponent<ProcessorViewProps> = ({processor, width}) => {
    const attrs: {[key: string]: any} = {}
    processor.attributes.forEach((attr) => {
        attrs[attr.name] = attr.value
    })
    const wipElmt = attrs.wip ? <span style={{color: 'darkblue'}}> (WIP)</span> : null
    return (
        <div className="Processor" style={{position: 'relative', width: width - 20, padding: 10, overflowY: 'auto'}}>
            <div style={{display: 'flex', flexDirection: 'row'}}>
                <div className="ProcessorImage" style={{width: 100,  marginRight: 10}}>
                    {
                        attrs.logo_url ? (
                            <img src={attrs.logo_url} style={{width: 100}} />
                        ) : (
                            <Build style={{paddingLeft: 10, paddingTop: 10, fontSize: 80}} />
                        )
                    }
                </div>
                <div className="ProcessorSecondColumn" style={{flex: 1}}>
                    <div className="ProcessorTitle">{attrs.label || attrs.name}{wipElmt}</div>
                    <div className="ProcessorDescription">{processor.help}</div>
                    <div>&nbsp;</div>
                    <div className="ProcessorParameters">
                        <ProcessorParametersView processor={processor} />
                    </div>
                    <div>&nbsp;</div>
                    <div className="ProcessorTags">
                        |&nbsp;{(processor.tags.map(t => t.tag) || []).map((tag, i) => <span key={i} className="ProcessorTag">{tag}&nbsp;|&nbsp;</span>)}
                    </div>
                </div>
            </div>
        </div>
    )
}

type ProcessorParametersViewProps = {
    processor: ComputeResourceSpecProcessor
}

const ProcessorParametersView: FunctionComponent<ProcessorParametersViewProps> = ({processor}) => {
    return (
        <div>
            <div>
                {processor.inputs.map((p, i) => <div key={i}>
                    {p.name} - {p.help}
                </div>)}
            </div>
            <div>
                {processor.outputs.map((p, i) => <div key={i}>
                    {p.name} - {p.help}
                </div>)}
            </div>
            <div>
                {processor.parameters.map((p, i) => <div key={i}>
                    {p.name} - {p.help}
                </div>)}
            </div>
        </div>
    )
}

export default ProcessorsView