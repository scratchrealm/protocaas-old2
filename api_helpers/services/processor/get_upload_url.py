import os
from ...core.protocaas_types import ProtocaasJob
from ._get_signed_upload_url import _get_signed_upload_url


async def get_upload_url(job: ProtocaasJob, output_name: str):
    aa = [x for x in job.outputFiles if x.name == output_name]
    if len(aa) == 0:
        raise Exception(f"No output with name {output_name}")
    
    object_key = f"protocaas-outputs/{job.jobId}/{output_name}"

    OUTPUT_BUCKET_URI = os.environ.get('OUTPUT_BUCKET_URI')
    if OUTPUT_BUCKET_URI is None:
        raise Exception('Environment variable not set: OUTPUT_BUCKET_URI')
    OUTPUT_BUCKET_CREDENTIALS = os.environ.get('OUTPUT_BUCKET_CREDENTIALS')
    if OUTPUT_BUCKET_CREDENTIALS is None:
        raise Exception('Environment variable not set: OUTPUT_BUCKET_CREDENTIALS')
    
    signed_upload_url = await _get_signed_upload_url(
        bucket_uri=OUTPUT_BUCKET_URI,
        bucket_credentials=OUTPUT_BUCKET_CREDENTIALS,
        object_key=object_key
    )

    return signed_upload_url