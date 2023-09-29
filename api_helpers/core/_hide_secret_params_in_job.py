from .protocaas_types import ProtocaasJob


def _hide_secret_params_in_job(job: ProtocaasJob):
    for param in job.inputParameters:
        processor_spec_param = next((x for x in job.processorSpec.parameters if x.name == param.name), None)
        if processor_spec_param is None:
            raise Exception(f"Processor spec parameter not found: {param.name}")
        if processor_spec_param.secret:
            param.value = None