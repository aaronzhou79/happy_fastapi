from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core.context import clear_context, set_tenant_id


class TenantMiddleware(BaseHTTPMiddleware):
    """多账套中间件，负责从请求中提取账套ID并设置到上下文中"""

    def __init__(
        self,
        app: ASGIApp,
        tenant_header: str = "X-Tenant-ID",
        tenant_query_param: str = "tenant_id",
        default_tenant: int | None = None
    ):
        super().__init__(app)
        self.tenant_header = tenant_header
        self.tenant_query_param = tenant_query_param
        self.default_tenant = default_tenant

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """多账套中间件，负责从请求中提取账套ID并设置到上下文中"""
        # 从请求中提取账套ID
        tenant_id = self._extract_tenant_id(request)

        # 设置账套ID到上下文
        set_tenant_id(tenant_id)

        try:
            # 处理请求
            return await call_next(request)
        finally:
            # 清理上下文
            clear_context()

    def _extract_tenant_id(self, request: Request) -> int | None:
        """从请求中提取账套ID"""
        # 1. 尝试从请求头中获取
        tenant_id = request.headers.get(self.tenant_header)
        if tenant_id:
            return int(tenant_id)

        # 2. 尝试从查询参数中获取
        tenant_id = request.query_params.get(self.tenant_query_param)
        if tenant_id:
            return int(tenant_id)

        # 4. 返回默认账套ID
        return self.default_tenant