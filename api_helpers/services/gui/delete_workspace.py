import time
from ...core.protocaas_types import ProtocaasWorkspace
from ...clients.db import delete_all_files_in_workspace, delete_all_jobs_in_workspace, delete_all_projects_in_workspace, delete_workspace as db_delete_workspace, update_workspace


async def delete_workspace(workspace: ProtocaasWorkspace):
    await delete_all_files_in_workspace(workspace.workspaceId)
    await delete_all_jobs_in_workspace(workspace.workspaceId)
    await delete_all_projects_in_workspace(workspace.workspaceId)
    await db_delete_workspace(workspace.workspaceId)