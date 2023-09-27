import boto3
import json


async def _get_signed_upload_url(*,
    bucket_uri: str,
    bucket_credentials: str,
    object_key: str
):
    creds = json.loads(bucket_credentials)
    access_key_id = creds['accessKeyId']
    secret_access_key = creds['secretAccessKey']
    endpoint = creds.get('endpoint', None)
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        endpoint_url=endpoint
    )

    bucket_name = _get_bucket_name_from_uri(bucket_uri)

    return s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': bucket_name,
            'Key': object_key
        },
        ExpiresIn=30 * 60 # 30 minutes
    )

def _get_bucket_name_from_uri(bucket_uri: str) -> str:
    if not bucket_uri:
        return ''
    return bucket_uri.split('?')[0].split('/')[2]