import contextvars

# 创建上下文变量
_tenant_id_var = contextvars.ContextVar("tenant_id", default=None)
_user_id_var = contextvars.ContextVar("user_id", default=None)


def set_tenant_id(tenant_id: int | None) -> None:
    """设置当前上下文的账套ID"""
    _tenant_id_var.set(tenant_id)  # type: ignore


def get_tenant_id() -> int | None:
    """获取当前上下文的账套ID"""
    return _tenant_id_var.get()


def set_user_id(user_id: int | None) -> None:
    """设置当前上下文的用户ID"""
    _user_id_var.set(user_id)  # type: ignore


def get_user_id() -> int | None:
    """获取当前上下文的用户ID"""
    return _user_id_var.get()


def clear_context() -> None:
    """清除上下文数据"""
    _tenant_id_var.set(None)
    _user_id_var.set(None)