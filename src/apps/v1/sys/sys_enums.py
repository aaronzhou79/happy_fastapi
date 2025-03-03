from src.common.enums import StrEnum


class NotificationCondition(StrEnum):
    """
    通知条件
    """
    SUCCESS = "success"
    FAILURE = "failure"
    ALWAYS = "always"


class NotificationType(StrEnum):
    """
    通知类型
    """
    SYSTEM = "SYSTEM"
    USER = "USER"

