from fastapi import FastAPI

from src.apps.v1.sys.service.permission import svr_permission
from src.database.db_session import AuditAsyncSession


async def init_permissions(session: AuditAsyncSession, app: FastAPI) -> None:
    """初始化权限数据"""
    await svr_permission.init_permission(session, app)
