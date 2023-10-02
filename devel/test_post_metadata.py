import os
import json
import requests


def main():
    dandi_api_key = os.environ['DANDI_STAGING_API_KEY']
    headers = {
        'Authorization': f'token {dandi_api_key}'
    }
    dandiset_id = '210194'
    file_path = f'sub-paired-english/sub-paired-english_ses-paired-english-m57-191105-160026_ecephys_desc-ms5-quicktest.nwb'
    staging = True

    assets_base_url = f'https://api{"-staging" if staging else ""}.dandiarchive.org/api/dandisets/{dandiset_id}/versions/draft/assets'
    assets_url = f'{assets_base_url}/?path={file_path}' 
        
    res = requests.get(assets_url, headers=headers)
    if res.status_code != 200:
        print(res.status_code)
        print(res.json())
        raise Exception('Failed to get assets')
    assets = res.json()['results']
    if len(assets) == 0:
        print('Asset not found')
        return
    if len(assets) > 1:
        print('More than one asset found')
    asset = assets[0]
    print(json.dumps(asset, indent=2))

    asset_url = f'{assets_base_url}/{asset["asset_id"]}/'

    res = requests.get(asset_url, headers=headers)
    if res.status_code != 200:
        print(res.status_code)
        print(res.json())
        raise Exception('Failed to get metadata for asset')
    metadata = res.json()
    print(json.dumps(metadata, indent=2))

    x = metadata['wasGeneratedBy']
    x.append({'test': 2})

    put_json = {
        "blob_id": asset["blob"],
        "metadata": metadata
    }

    res = requests.put(asset_url, headers=headers, json=put_json)
    if res.status_code != 200:
        print(res.status_code)
        print(res.json())
        raise Exception('Failed to update metadata for asset')
    print(json.dumps(res.json(), indent=2))

if __name__ == '__main__':
    main()