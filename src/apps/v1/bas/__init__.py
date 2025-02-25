from fastapi import APIRouter

from .api.demo import router as demo_router

router = APIRouter(prefix="/bas")

router.include_router(demo_router)
