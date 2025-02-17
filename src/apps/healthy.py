# @File    : healthy.py
# @Software: Cursor
# @Description: 健康检查

from fastapi import APIRouter

router = APIRouter(prefix="/healthy")

@router.get("/")
async def healthy() -> dict:
    """
    健康检查
    """
    return {"message": "ok"}
