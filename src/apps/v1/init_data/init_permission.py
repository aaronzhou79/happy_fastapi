from fastapi import FastAPI

from src.apps.v1.sys.service.permission import svr_permission


async def init_permissions(app: FastAPI) -> None:
    """初始化权限数据"""
    await svr_permission.init_permission(app)
