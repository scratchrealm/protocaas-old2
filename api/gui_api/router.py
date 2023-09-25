from fastapi import APIRouter
from .create_job_routes import router as create_job_router
from .project_routes import router as project_router
from .workspace_routes import router as workspace_router
from .compute_resource_routes import router as compute_resource_router
from .file_routes import router as file_router
from .job_routes import router as job_router

router = APIRouter()

router.include_router(create_job_router)
router.include_router(project_router)
router.include_router(workspace_router)
router.include_router(compute_resource_router)
router.include_router(file_router)
router.include_router(job_router)