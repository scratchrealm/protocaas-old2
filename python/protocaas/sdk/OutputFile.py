import requests
from ._post_api_request import _post_api_request


class OutputFile:
    def __init__(self, *, name: str, job_id: str, job_private_key: str) -> None:
        self._name = name
        self._job_id = job_id
        self._job_private_key = job_private_key
        self._was_set = False
    def set(self, local_file_path: str):
        req = {
            'type': 'processor.getOutputUploadUrl',
            'jobId': self._job_id,
            'jobPrivateKey': self._job_private_key,
            'outputName': self._name
        }
        resp = _post_api_request(req)
        upload_url = resp['uploadUrl'] # This will be a presigned AWS S3 URL

        # Upload the file to the URL
        with open(local_file_path, 'rb') as f:
            resp_upload = requests.put(upload_url, data=f)
            if resp_upload.status_code != 200:
                print(upload_url)
                raise Exception(f'Error uploading file to bucket ({resp_upload.status_code}) {resp_upload.reason}: {resp_upload.text}')
        
        self._was_set = True