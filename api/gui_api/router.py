from fastapi import APIRouter
from .create_job_handler import router as create_job_router
from .project_handlers import router as project_router
from .workspace_handlers import router as workspace_router
from .compute_resource_handlers import router as compute_resource_router

router = APIRouter()

router.include_router(create_job_router)
router.include_router(project_router)
router.include_router(workspace_router)
router.include_router(compute_resource_router)

