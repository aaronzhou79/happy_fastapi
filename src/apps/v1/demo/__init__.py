from fastapi import APIRouter

from .api.demo import demo_api

router = APIRouter(prefix="/demo")

router.include_router(demo_api.router)
