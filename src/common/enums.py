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

    pass


class StrEnum(_EnumBase, str, Enum):
    """字符串枚举"""

    pass


class UserStatus(StrEnum):
    ACTIVE = "已激活"
    INACTIVE = "未激活"
    SUSPENDED = "已禁用"
