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


class OperaLogCipherType(IntEnum):
    """操作日志加密类型"""

    aes = 0
    md5 = 1
    itsdangerous = 2
    plan = 3


class StatusType(IntEnum):
    """状态类型"""

    disable = 0
    enable = 1


class LoginLogStatusType(IntEnum):
    """登陆日志状态"""

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
