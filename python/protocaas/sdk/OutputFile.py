import requests
from ..common._api_request import _processor_get_api_request


class OutputFile:
    def __init__(self, *, name: str, job_id: str, job_private_key: str) -> None:
        self._name = name
        self._job_id = job_id
        self._job_private_key = job_private_key
        self._was_set = False
    def set(self, local_file_path: str):
        url_path = f'/api/processor/jobs/{self._job_id}/outputs/{self._name}/upload_url'
        headers = {
            'job-private-key': self._job_private_key
        }
        resp = _processor_get_api_request(
            url_path=url_path,
            headers=headers
        )
        upload_url = resp['uploadUrl'] # This will be a presigned AWS S3 URL

        # Upload the file to the URL
        with open(local_file_path, 'rb') as f:
            resp_upload = requests.put(upload_url, data=f)
            if resp_upload.status_code != 200:
                print(upload_url)
                raise Exception(f'Error uploading file to bucket ({resp_upload.status_code}) {resp_upload.reason}: {resp_upload.text}')
        
        self._was_set = True