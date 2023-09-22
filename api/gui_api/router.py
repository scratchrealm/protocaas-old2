from fastapi import APIRouter
from .create_job_endpoint import router as create_job_router

router = APIRouter()

router.include_router(create_job_router)

