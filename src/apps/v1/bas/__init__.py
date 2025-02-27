from fastapi import APIRouter

from .api.code_setting import code_setting_api
from .api.code_trace import code_trace_api
from .api.demo import router as demo_router

router = APIRouter(prefix="/bas")

router.include_router(demo_router)
router.include_router(code_setting_api.router)
router.include_router(code_trace_api.router)