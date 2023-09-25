import requests


class InputFile:
    def __init__(self, *, name: str, url: str) -> None:
        self._name = name
        self._url = url
    def get_url(self) -> str:
        return self._url
    def download(self, dest_file_path: str):
        url = self._url
        print(f'Downloading {url} to {dest_file_path}')
        # stream the download
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            raise Exception(f'Problem downloading {url}')
        with open(dest_file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)