from __future__ import annotations

from enum import Enum
from enum import IntEnum as SourceIntEnum
from typing import Type


class _EnumBase(Enum):
    @classmethod
    def get_member_keys(cls: Type[Enum]) -> list[str]:
        return [name for name in cls.__members__.keys()]

    @classmethod
    def get_member_values(cls: Type[Enum]) -> list:
        return [item.value for item in cls.__members__.values()]


class IntEnum(_EnumBase, SourceIntEnum):
    """整型枚举"""


class StrEnum(_EnumBase, str, Enum):
    """字符串枚举"""


class HookTypeEnum(StrEnum):
    """钩子类型"""

    before_create = "before_create"
    after_create = "after_create"
    before_update = "before_update"
    after_update = "after_update"
    before_delete = "before_delete"
    after_delete = "after_delete"


class OperaLogCipherType(IntEnum):
    """操作日志加密类型"""

    aes = 0
    md5 = 1
    itsdangerous = 2
    plan = 3


class LoginLogStatusType(IntEnum):
    """登陆日志状态"""

    fail = 0
    success = 1


class RoleStatusType(StrEnum):
    """角色状态"""

    active = "启用"
    inactive = "禁用"


class PermissionType(StrEnum):
    """权限类型"""

    menu = "menu"
    api = "api"
    data = "data"


class OperaLogStatusType(IntEnum):
    """操作日志状态"""

    fail = 0
    success = 1


class UserEmpType(StrEnum):
    """用户员工类型"""

    admin = "管理员"
    staff = "员工"
    sales = "销售"
    finance = "财务"
    hr = "人事"
    it = "IT"


class UserStatus(StrEnum):
    """用户状态"""

    ACTIVE = "已激活"
    INACTIVE = "未激活"
    SUSPENDED = "已禁用"
