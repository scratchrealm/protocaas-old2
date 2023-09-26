import time
from ...core.protocaas_types import ProtocaasProject
from ...clients.db import delete_all_files_in_project, delete_all_jobs_in_project, delete_project as db_delete_project, update_workspace


async def delete_project(project: ProtocaasProject):
    await delete_all_files_in_project(project.projectId)
    await delete_all_jobs_in_project(project.projectId)
    await db_delete_project(project.projectId)

    await update_workspace(project.workspaceId, {
        'timestampModified': time.time()
    })