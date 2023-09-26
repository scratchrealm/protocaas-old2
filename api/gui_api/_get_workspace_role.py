from ..common.protocaas_types import ProtocaasWorkspace


def _get_workspace_role(workspace: ProtocaasWorkspace, user_id: str):
    if user_id.startswith('admin|'):
        return 'admin'
    if user_id:
        if workspace.ownerId == user_id:
            return 'admin'
        user = next((x for x in workspace.users if x.userId == user_id), None)
        if user:
            return user.role
    if workspace.publiclyReadable:
        return 'viewer'
    else:
        return 'none'