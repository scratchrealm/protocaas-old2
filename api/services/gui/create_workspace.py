import time
from ...core.protocaas_types import ProtocaasWorkspace
from ...core._create_random_id import _create_random_id
from ...clients.db import insert_workspace


async def create_workspace(*, name: str, user_id: str):
    workspace_id = _create_random_id(8)
    workspace = ProtocaasWorkspace(
        workspaceId=workspace_id,
        ownerId=user_id,
        name=name,
        description='',
        users=[],
        publiclyReadable=True,
        listed=False,
        timestampCreated=time.time(),
        timestampModified=time.time()
    )
    await insert_workspace(workspace)
    return workspace_id