# @File    : healthy.py
# @Software: Cursor
# @Description: 健康检查

from fastapi import APIRouter

router = APIRouter(prefix="/healthy", tags=["健康检查"])

@router.get("/")
async def healthy() -> dict:
    """
    健康检查
    """
    return {"message": "ok"}
