
from contextvars import ContextVar

from fastapi import Request

_request_ctx_var: ContextVar[Request] = ContextVar("_request_ctx_var")

__all__ = ["_request_ctx_var", "UserState"]


class UserState():
    """用户状态"""

    """
    获取审计用户类
    """
    @classmethod
    def get_current_user_id(cls) -> int:
        """获取当前请求用户ID"""
        try:
            request = _request_ctx_var.get()

            if request and hasattr(request, 'user'):
                return getattr(request.user, "identity", 0)
        except Exception as e:
            print(f"获取当前请求用户ID失败: {str(getattr(e, 'data', e))}")
        return 0