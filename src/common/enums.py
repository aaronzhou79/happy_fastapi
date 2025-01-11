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


class OperaLogCipher(IntEnum):
    """操作日志加密类型"""

    AES = 0
    MD5 = 1
    ITSDANGEROUS = 2
    PLAN = 3


class LoginLogStatus(IntEnum):
    """登陆日志状态"""

    FAIL = 0
    SUCCESS = 1


class RoleStatus(StrEnum):
    """角色状态"""

    ACTIVE = "启用"
    INACTIVE = "禁用"


class PermissionType(StrEnum):
    """权限类型"""

    MENU = "menu"
    API = "api"
    DATA = "data"


class PermissionRuleStatus(StrEnum):
    """权限规则状态"""

    ENABLE = "启用"
    DISABLE = "禁用"


class OperaLogStatus(IntEnum):
    """操作日志状态"""

    FAIL = 0
    SUCCESS = 1


class UserEmpType(StrEnum):
    """用户员工类型"""

    ADMIN = "管理员"
    STAFF = "员工"
    SALES = "销售"
    FINANCE = "财务"
    HR = "人事"
    IT = "IT"


class UserStatus(StrEnum):
    """用户状态"""

    ACTIVE = "已激活"
    INACTIVE = "未激活"
    SUSPENDED = "已禁用"
