from ._get_mongo_client import _get_mongo_client


def _remove_detached_files_and_jobs(project_id: str):
    client = _get_mongo_client()
    files_collection = client['protocaas']['files']
    jobs_collection = client['protocaas']['jobs']

    files = list(files_collection.find({
        'projectId': project_id
    }))
    jobs = list(jobs_collection.find({
        'projectId': project_id
    }))

    something_changed = True
    while something_changed:
        file_ids = set(x['fileId'] for x in files)
        job_ids = set(x['jobId'] for x in jobs)

        job_ids_to_delete = set()
        for job in jobs:
            if any(x not in file_ids for x in job['inputFileIds']):
                job_ids_to_delete.add(job['jobId'])
            if 'outputFileIds' in job:
                if any(x not in file_ids for x in job['outputFileIds']):
                    job_ids_to_delete.add(job['jobId'])
        file_ids_to_delete = set()
        for file in files:
            if 'jobId' in file:
                if file['jobId'] not in job_ids:
                    file_ids_to_delete.add(file['fileId'])
        something_changed = False
        if len(job_ids_to_delete) > 0:
            something_changed = True
            jobs_collection.delete_many({
                'jobId': {'$in': list(job_ids_to_delete)}
            })
            jobs = [x for x in jobs if x['jobId'] not in job_ids_to_delete]
        if len(file_ids_to_delete) > 0:
            something_changed = True
            files_collection.delete_many({
                'fileId': {'$in': list(file_ids_to_delete)}
            })
            files = [x for x in files if x['fileId'] not in file_ids_to_delete]